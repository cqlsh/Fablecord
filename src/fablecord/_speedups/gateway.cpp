/*
The MIT License (MIT)

Copyright (c) 2026-present cqlsh

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
*/

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <climits>
#include <cstring>

namespace {

PyDoc_STRVAR(peek_doc,
"peek(payload, /)\n"
"--\n"
"\n"
"Reads the envelope of a gateway payload from its first bytes, without\n"
"parsing it, and returns the opcode, the sequence number and the event\n"
"name as a tuple. The sequence number and the name are None on anything\n"
"but a dispatch. The name is an interned string, so every payload of an\n"
"event returns the same object.\n"
"\n"
"Returns None when the payload does not start with the keys t, s and op\n"
"in the order Discord writes them, so the caller can parse it instead.");

class Payload
{
public:
    const unsigned char *begin;
    const unsigned char *end;

    Payload() : begin(nullptr), end(nullptr), view(), owned(false)
    {
    }

    ~Payload()
    {
        if (owned) {
            PyBuffer_Release(&view);
        }
    }

    Payload(const Payload &) = delete;
    Payload &operator=(const Payload &) = delete;

    bool open(PyObject *object)
    {
        if (PyBytes_Check(object)) {
            begin = reinterpret_cast<const unsigned char *>(PyBytes_AS_STRING(object));
            end = begin + PyBytes_GET_SIZE(object);

            return true;
        }

        if (PyObject_GetBuffer(object, &view, PyBUF_SIMPLE) < 0) {
            return false;
        }

        begin = static_cast<const unsigned char *>(view.buf);
        end = begin + view.len;
        owned = true;

        return true;
    }

private:
    Py_buffer view;
    bool owned;
};

bool is_name_byte(unsigned char c)
{
    return (c >= 'A' && c <= 'Z') || c == '_' || (c >= '0' && c <= '9');
}

PyObject *peek(PyObject *Py_UNUSED(module), PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 1) {
        PyErr_SetString(PyExc_TypeError, "peek() takes exactly one argument: payload");
        return nullptr;
    }

    Payload payload;
    if (!payload.open(args[0])) {
        return nullptr;
    }

    const unsigned char *p = payload.begin;
    const unsigned char *end = payload.end;
    const unsigned char *name = nullptr;
    Py_ssize_t name_size = 0;
    long long sequence = 0;
    bool has_sequence = false;
    long op = 0;

    if (end - p < 5 || std::memcmp(p, "{\"t\":", 5) != 0) {
        Py_RETURN_NONE;
    }
    p += 5;

    if (end - p >= 4 && std::memcmp(p, "null", 4) == 0) {
        p += 4;
    } else if (p < end && *p == '"') {
        p++;
        name = p;
        while (p < end && is_name_byte(*p)) {
            p++;
        }
        name_size = p - name;
        if (name_size == 0 || p >= end || *p != '"') {
            Py_RETURN_NONE;
        }
        p++;
    } else {
        Py_RETURN_NONE;
    }

    if (end - p < 5 || std::memcmp(p, ",\"s\":", 5) != 0) {
        Py_RETURN_NONE;
    }
    p += 5;

    if (end - p >= 4 && std::memcmp(p, "null", 4) == 0) {
        p += 4;
    } else {
        const unsigned char *digits = p;
        while (p < end && *p >= '0' && *p <= '9') {
            int digit = *p - '0';
            if (sequence > (LLONG_MAX - digit) / 10) {
                Py_RETURN_NONE;
            }
            sequence = sequence * 10 + digit;
            p++;
        }
        if (p == digits) {
            Py_RETURN_NONE;
        }
        has_sequence = true;
    }

    if (end - p < 6 || std::memcmp(p, ",\"op\":", 6) != 0) {
        Py_RETURN_NONE;
    }
    p += 6;

    const unsigned char *digits = p;
    while (p < end && *p >= '0' && *p <= '9') {
        if (op > 99) {
            Py_RETURN_NONE;
        }
        op = op * 10 + (*p - '0');
        p++;
    }
    if (p == digits) {
        Py_RETURN_NONE;
    }

    PyObject *name_object;
    if (name == nullptr) {
        name_object = Py_NewRef(Py_None);
    } else {
        name_object = PyUnicode_FromStringAndSize(reinterpret_cast<const char *>(name), name_size);
        if (name_object == nullptr) {
            return nullptr;
        }
        PyUnicode_InternInPlace(&name_object);
    }

    PyObject *sequence_object = has_sequence ? PyLong_FromLongLong(sequence) : Py_NewRef(Py_None);
    if (sequence_object == nullptr) {
        Py_DECREF(name_object);
        return nullptr;
    }

    PyObject *op_object = PyLong_FromLong(op);
    if (op_object == nullptr) {
        Py_DECREF(name_object);
        Py_DECREF(sequence_object);
        return nullptr;
    }

    PyObject *result = PyTuple_New(3);
    if (result == nullptr) {
        Py_DECREF(name_object);
        Py_DECREF(sequence_object);
        Py_DECREF(op_object);
        return nullptr;
    }
    PyTuple_SET_ITEM(result, 0, op_object);
    PyTuple_SET_ITEM(result, 1, sequence_object);
    PyTuple_SET_ITEM(result, 2, name_object);

    return result;
}

PyMethodDef methods[] = {
    {"peek", reinterpret_cast<PyCFunction>(reinterpret_cast<void (*)()>(peek)), METH_FASTCALL, peek_doc},
    {nullptr, nullptr, 0, nullptr}
};

PyDoc_STRVAR(module_doc, "C++ helpers for fablecord.gateway.decoder, used when they could be built.");

PyModuleDef_Slot slots[] = {
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {0, nullptr}
};

PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "fablecord._speedups.gateway",
    module_doc,
    0,
    methods,
    slots,
    nullptr,
    nullptr,
    nullptr
};

}

PyMODINIT_FUNC PyInit_gateway(void)
{
    return PyModuleDef_Init(&module);
}