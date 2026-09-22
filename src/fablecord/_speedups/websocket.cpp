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
#include <cstdint>
#include <cstring>

namespace {

struct websocket_state
{
    PyObject *append_name;
};

class Borrowed
{
public:
    const unsigned char *bytes;
    Py_ssize_t size;

    Borrowed() : bytes(nullptr), size(0), view(), owned(false)
    {
    }

    ~Borrowed()
    {
        if (owned) {
            PyBuffer_Release(&view);
        }
    }

    Borrowed(const Borrowed &) = delete;
    Borrowed &operator=(const Borrowed &) = delete;

    bool open(PyObject *object)
    {
        if (PyObject_GetBuffer(object, &view, PyBUF_SIMPLE) < 0) {
            return false;
        }

        bytes = static_cast<const unsigned char *>(view.buf);
        size = view.len;
        owned = true;

        return true;
    }

private:
    Py_buffer view;
    bool owned;
};

PyDoc_STRVAR(frame_doc,
"frame(opcode, key, payload, /)\n"
"--\n"
"\n"
"Builds one masked client frame: the header, the four key bytes and the\n"
"payload XORed with the key, in a single bytes object.\n"
"\n"
"opcode is the frame type, 0 to 15, sent with the FIN bit set. key is the\n"
"32-bit mask as an integer, its big-endian bytes go on the wire. payload is\n"
"any bytes-like object.");

PyObject *frame(PyObject *Py_UNUSED(module), PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 3) {
        PyErr_SetString(PyExc_TypeError, "frame() takes exactly three arguments: opcode, key and payload");
        return nullptr;
    }

    long opcode = PyLong_AsLong(args[0]);
    if (opcode == -1 && PyErr_Occurred()) {
        return nullptr;
    }
    if (opcode < 0 || opcode > 15) {
        PyErr_SetString(PyExc_ValueError, "opcode must be between 0 and 15");
        return nullptr;
    }

    unsigned long long key = PyLong_AsUnsignedLongLong(args[1]);
    if (key == static_cast<unsigned long long>(-1) && PyErr_Occurred()) {
        return nullptr;
    }
    if (key > 0xFFFFFFFFULL) {
        PyErr_SetString(PyExc_ValueError, "key must fit in 32 bits");
        return nullptr;
    }

    Borrowed payload;
    if (!payload.open(args[2])) {
        return nullptr;
    }

    Py_ssize_t size = payload.size;
    if (size > PY_SSIZE_T_MAX - 14) {
        PyErr_SetString(PyExc_OverflowError, "payload is too large for one frame");
        return nullptr;
    }

    Py_ssize_t header_size = size < 126 ? 2 : size < 65536 ? 4 : 10;
    PyObject *result = PyBytes_FromStringAndSize(nullptr, header_size + 4 + size);
    if (result == nullptr) {
        return nullptr;
    }

    unsigned char *out = reinterpret_cast<unsigned char *>(PyBytes_AS_STRING(result));
    out[0] = static_cast<unsigned char>(0x80 | opcode);

    if (size < 126) {
        out[1] = static_cast<unsigned char>(0x80 | size);
    } else if (size < 65536) {
        out[1] = 0xFE;
        out[2] = static_cast<unsigned char>(size >> 8);
        out[3] = static_cast<unsigned char>(size);
    } else {
        out[1] = 0xFF;
        for (int i = 0; i < 8; i++) {
            out[2 + i] = static_cast<unsigned char>(static_cast<std::uint64_t>(size) >> (56 - 8 * i));
        }
    }

    unsigned char *mask = out + header_size;
    mask[0] = static_cast<unsigned char>(key >> 24);
    mask[1] = static_cast<unsigned char>(key >> 16);
    mask[2] = static_cast<unsigned char>(key >> 8);
    mask[3] = static_cast<unsigned char>(key);

    std::uint64_t pattern;
    std::memcpy(&pattern, mask, 4);
    std::memcpy(reinterpret_cast<unsigned char *>(&pattern) + 4, mask, 4);

    const unsigned char *src = payload.bytes;
    unsigned char *dst = mask + 4;
    Py_ssize_t i = 0;

    for (; i + 8 <= size; i += 8) {
        std::uint64_t word;
        std::memcpy(&word, src + i, 8);
        word ^= pattern;
        std::memcpy(dst + i, &word, 8);
    }

    for (; i < size; i++) {
        dst[i] = src[i] ^ mask[i & 3];
    }

    return result;
}

PyDoc_STRVAR(parse_doc,
"parse(buffer, offset, max_size, messages, /)\n"
"--\n"
"\n"
"Delivers every whole, unmasked text or binary frame that starts at offset\n"
"into messages, a deque, and returns the offset of the first frame it did\n"
"not take: an incomplete one, a control frame, a fragment, a masked frame,\n"
"one above max_size, one whose extended length is not minimal or does not\n"
"fit, or text that is not UTF-8. The caller handles that frame itself. A\n"
"negative max_size accepts any length.");

PyObject *parse(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 4) {
        PyErr_SetString(PyExc_TypeError, "parse() takes exactly four arguments: buffer, offset, max_size and messages");
        return nullptr;
    }

    websocket_state *state = static_cast<websocket_state *>(PyModule_GetState(module));
    if (state == nullptr || state->append_name == nullptr) {
        PyErr_SetString(PyExc_SystemError, "fablecord._speedups.websocket is not initialised");
        return nullptr;
    }

    Py_ssize_t offset = PyLong_AsSsize_t(args[1]);
    if (offset == -1 && PyErr_Occurred()) {
        return nullptr;
    }

    Py_ssize_t max_size = PyLong_AsSsize_t(args[2]);
    if (max_size == -1 && PyErr_Occurred()) {
        return nullptr;
    }

    Borrowed frames;
    if (!frames.open(args[0])) {
        return nullptr;
    }

    const unsigned char *buffer = frames.bytes;
    Py_ssize_t total = frames.size;
    PyObject *messages = args[3];

    if (offset < 0 || offset > total) {
        PyErr_SetString(PyExc_ValueError, "offset is outside the buffer");
        return nullptr;
    }

    while (total - offset >= 2) {
        unsigned char first = buffer[offset];
        unsigned char second = buffer[offset + 1];

        if ((first != 0x81 && first != 0x82) || (second & 0x80)) {
            break;
        }

        Py_ssize_t length = second & 0x7F;
        Py_ssize_t start = offset + 2;

        if (length == 126) {
            if (total - start < 2) {
                break;
            }
            length = static_cast<Py_ssize_t>(buffer[start]) << 8 | buffer[start + 1];
            if (length < 126) {
                break;
            }
            start += 2;
        } else if (length == 127) {
            if (total - start < 8) {
                break;
            }
            std::uint64_t wide = 0;
            for (int i = 0; i < 8; i++) {
                wide = wide << 8 | buffer[start + i];
            }
            if (wide < 65536 || wide > static_cast<std::uint64_t>(PY_SSIZE_T_MAX)) {
                break;
            }
            length = static_cast<Py_ssize_t>(wide);
            start += 8;
        }

        if ((max_size >= 0 && length > max_size) || length > total - start) {
            break;
        }

        PyObject *item;
        if (first == 0x81) {
            item = PyUnicode_DecodeUTF8(reinterpret_cast<const char *>(buffer) + start, length, nullptr);
            if (item == nullptr) {
                if (PyErr_ExceptionMatches(PyExc_UnicodeDecodeError)) {
                    PyErr_Clear();
                    break;
                }
                return nullptr;
            }
        } else {
            item = PyBytes_FromStringAndSize(reinterpret_cast<const char *>(buffer) + start, length);
            if (item == nullptr) {
                return nullptr;
            }
        }

        PyObject *appended = PyObject_CallMethodOneArg(messages, state->append_name, item);
        Py_DECREF(item);
        if (appended == nullptr) {
            return nullptr;
        }
        Py_DECREF(appended);

        offset = start + length;
    }

    return PyLong_FromSsize_t(offset);
}

PyMethodDef methods[] = {
    {"frame", reinterpret_cast<PyCFunction>(reinterpret_cast<void (*)()>(frame)), METH_FASTCALL, frame_doc},
    {"parse", reinterpret_cast<PyCFunction>(reinterpret_cast<void (*)()>(parse)), METH_FASTCALL, parse_doc},
    {nullptr, nullptr, 0, nullptr}
};

PyDoc_STRVAR(module_doc, "C++ helpers for fablecord.net.websocket, used when they could be built.");

int websocket_exec(PyObject *module)
{
    websocket_state *state = static_cast<websocket_state *>(PyModule_GetState(module));

    state->append_name = PyUnicode_InternFromString("append");
    return state->append_name == nullptr ? -1 : 0;
}

int websocket_traverse(PyObject *module, visitproc visit, void *arg)
{
    websocket_state *state = static_cast<websocket_state *>(PyModule_GetState(module));

    Py_VISIT(state->append_name);
    return 0;
}

int websocket_clear(PyObject *module)
{
    websocket_state *state = static_cast<websocket_state *>(PyModule_GetState(module));

    Py_CLEAR(state->append_name);
    return 0;
}

void websocket_free(void *module)
{
    websocket_clear(static_cast<PyObject *>(module));
}

PyModuleDef_Slot slots[] = {
    {Py_mod_exec, reinterpret_cast<void *>(websocket_exec)},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {0, nullptr}
};

PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "fablecord._speedups.websocket",
    module_doc,
    sizeof(websocket_state),
    methods,
    slots,
    websocket_traverse,
    websocket_clear,
    websocket_free
};

}

PyMODINIT_FUNC PyInit_websocket(void)
{
    return PyModuleDef_Init(&module);
}