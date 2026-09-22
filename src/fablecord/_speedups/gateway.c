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
#include <limits.h>
#include <string.h>

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

static int is_name_byte(unsigned char c)
{
    return (c >= 'A' && c <= 'Z') || c == '_' || (c >= '0' && c <= '9');
}

static PyObject *peek(PyObject *Py_UNUSED(module), PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 1) {
        PyErr_SetString(PyExc_TypeError, "peek() takes exactly one argument: payload");
        return NULL;
    }

    

    Py_buffer view;
    const unsigned char *p;
    const unsigned char *end;
    bool owned = false;

        auto other = [&]() -> PyObject *
    {  
        if (owned)
        {
            PyBuffer_Release(&view);
        }
        Py_RETURN_NONE;
    };

    auto fail = [&]() -> PyObject *
    {
        if (owned)
        {
            PyBuffer_Release(&view);
        }
        return nullptr;
    };

    if (PyBytes_Check(args[0])) {
        p = (const unsigned char *)PyBytes_AS_STRING(args[0]);
        end = p + PyBytes_GET_SIZE(args[0]);
    } else {
        if (PyObject_GetBuffer(args[0], &view, PyBUF_SIMPLE) < 0) {
            return NULL;
        }
        p = (const unsigned char *)view.buf;
        end = p + view.len;
        owned = true;
    }

    const unsigned char *name = NULL;
    Py_ssize_t name_size = 0;
    long long sequence = 0;
    int has_sequence = 0;
    long op = 0;

    if (end - p < 5 || memcmp(p, "{\"t\":", 5) != 0) {
        return other();
    }
    p += 5;

    if (end - p >= 4 && memcmp(p, "null", 4) == 0) {
        p += 4;
    } else if (p < end && *p == '"') {
        p++;
        name = p;
        while (p < end && is_name_byte(*p)) {
            p++;
        }
        name_size = p - name;
        if (name_size == 0 || p >= end || *p != '"') {
            return other();
        }
        p++;
    } else {
        return other();
    }

    if (end - p < 5 || memcmp(p, ",\"s\":", 5) != 0) {
        return other();
    }
    p += 5;

    if (end - p >= 4 && memcmp(p, "null", 4) == 0) {
        p += 4;
    } else {
        const unsigned char *digits = p;
        while (p < end && *p >= '0' && *p <= '9') {
            int digit = *p - '0';
            if (sequence > (LLONG_MAX - digit) / 10) {
                return other();
            }
            sequence = sequence * 10 + digit;
            p++;
        }
        if (p == digits) {
            return other();
        }
        has_sequence = 1;
    }

    if (end - p < 6 || memcmp(p, ",\"op\":", 6) != 0) {
        return other();
    }
    p += 6;

    const unsigned char *digits = p;
    while (p < end && *p >= '0' && *p <= '9') {
        if (op > 99) {
            return other();
        }
        op = op * 10 + (*p - '0');
        p++;
    }
    if (p == digits) {
        return other();
    }

    PyObject *name_object;
    if (name == NULL) {
        name_object = Py_NewRef(Py_None);
    } else {
        name_object = PyUnicode_FromStringAndSize((const char *)name, name_size);
        if (name_object == NULL) {
            return fail();
        }
        PyUnicode_InternInPlace(&name_object);
    }

    PyObject *sequence_object = has_sequence ? PyLong_FromLongLong(sequence) : Py_NewRef(Py_None);
    if (sequence_object == NULL) {
        Py_DECREF(name_object);
        return fail();
    }

    PyObject *op_object = PyLong_FromLong(op);
    if (op_object == NULL) {
        Py_DECREF(name_object);
        Py_DECREF(sequence_object);
        return fail();
    }

    PyObject *result = PyTuple_New(3);
    if (result == NULL) {
        Py_DECREF(name_object);
        Py_DECREF(sequence_object);
        Py_DECREF(op_object);
        return fail();
    }
    PyTuple_SET_ITEM(result, 0, op_object);
    PyTuple_SET_ITEM(result, 1, sequence_object);
    PyTuple_SET_ITEM(result, 2, name_object);

    if (owned) {
        PyBuffer_Release(&view);
    }
    return fail();
}

static PyMethodDef methods[] = {
    {"peek", (PyCFunction)(void (*)(void))peek, METH_FASTCALL, peek_doc},
    {NULL, NULL, 0, NULL}
};

PyDoc_STRVAR(module_doc, "C helpers for fablecord.gateway.decoder, used when they could be built.");

static PyModuleDef_Slot slots[] = {
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {0, NULL}
};

static struct PyModuleDef module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "fablecord._speedups.gateway",
    .m_doc = module_doc,
    .m_size = 0,
    .m_methods = methods,
    .m_slots = slots
};

PyMODINIT_FUNC PyInit_gateway(void)
{
    return PyModuleDef_Init(&module);
}