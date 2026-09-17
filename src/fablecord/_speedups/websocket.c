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
#include <stdint.h>
#include <string.h>

typedef struct {
    PyObject *append_name;
} websocket_state;

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

static PyObject *frame(PyObject *Py_UNUSED(module), PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 3) {
        PyErr_SetString(PyExc_TypeError, "frame() takes exactly three arguments: opcode, key and payload");
        return NULL;
    }

    long opcode = PyLong_AsLong(args[0]);
    if (opcode == -1 && PyErr_Occurred()) {
        return NULL;
    }
    if (opcode < 0 || opcode > 15) {
        PyErr_SetString(PyExc_ValueError, "opcode must be between 0 and 15");
        return NULL;
    }

    unsigned long long key = PyLong_AsUnsignedLongLong(args[1]);
    if (key == (unsigned long long)-1 && PyErr_Occurred()) {
        return NULL;
    }
    if (key > 0xFFFFFFFFULL) {
        PyErr_SetString(PyExc_ValueError, "key must fit in 32 bits");
        return NULL;
    }

    Py_buffer payload;
    if (PyObject_GetBuffer(args[2], &payload, PyBUF_SIMPLE) < 0) {
        return NULL;
    }

    Py_ssize_t size = payload.len;
    if (size > PY_SSIZE_T_MAX - 14) {
        PyBuffer_Release(&payload);
        PyErr_SetString(PyExc_OverflowError, "payload is too large for one frame");
        return NULL;
    }
    Py_ssize_t header_size = size < 126 ? 2 : size < 65536 ? 4 : 10;
    PyObject *result = PyBytes_FromStringAndSize(NULL, header_size + 4 + size);
    if (result == NULL) {
        PyBuffer_Release(&payload);
        return NULL;
    }

    unsigned char *out = (unsigned char *)PyBytes_AS_STRING(result);
    out[0] = (unsigned char)(0x80 | opcode);

    if (size < 126) {
        out[1] = (unsigned char)(0x80 | size);
    } else if (size < 65536) {
        out[1] = 0xFE;
        out[2] = (unsigned char)(size >> 8);
        out[3] = (unsigned char)size;
    } else {
        out[1] = 0xFF;
        for (int i = 0; i < 8; i++) {
            out[2 + i] = (unsigned char)((uint64_t)size >> (56 - 8 * i));
        }
    }

    unsigned char *mask = out + header_size;
    mask[0] = (unsigned char)(key >> 24);
    mask[1] = (unsigned char)(key >> 16);
    mask[2] = (unsigned char)(key >> 8);
    mask[3] = (unsigned char)key;

    uint64_t pattern;
    memcpy(&pattern, mask, 4);
    memcpy((unsigned char *)&pattern + 4, mask, 4);

    const unsigned char *src = (const unsigned char *)payload.buf;
    unsigned char *dst = mask + 4;
    Py_ssize_t i = 0;

    for (; i + 8 <= size; i += 8) {
        uint64_t word;
        memcpy(&word, src + i, 8);
        word ^= pattern;
        memcpy(dst + i, &word, 8);
    }

    for (; i < size; i++) {
        dst[i] = src[i] ^ mask[i & 3];
    }

    PyBuffer_Release(&payload);
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

static PyObject *parse(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 4) {
        PyErr_SetString(PyExc_TypeError, "parse() takes exactly four arguments: buffer, offset, max_size and messages");
        return NULL;
    }

    websocket_state *state = (websocket_state *)PyModule_GetState(module);
    if (state == NULL || state->append_name == NULL) {
        PyErr_SetString(PyExc_SystemError, "fablecord._speedups.websocket is not initialised");
        return NULL;
    }

    Py_ssize_t offset = PyLong_AsSsize_t(args[1]);
    if (offset == -1 && PyErr_Occurred()) {
        return NULL;
    }

    Py_ssize_t max_size = PyLong_AsSsize_t(args[2]);
    if (max_size == -1 && PyErr_Occurred()) {
        return NULL;
    }

    Py_buffer view;
    if (PyObject_GetBuffer(args[0], &view, PyBUF_SIMPLE) < 0) {
        return NULL;
    }

    const unsigned char *buffer = (const unsigned char *)view.buf;
    Py_ssize_t total = view.len;
    PyObject *messages = args[3];

    if (offset < 0 || offset > total) {
        PyBuffer_Release(&view);
        PyErr_SetString(PyExc_ValueError, "offset is outside the buffer");
        return NULL;
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
            length = (Py_ssize_t)buffer[start] << 8 | buffer[start + 1];
            if (length < 126) {
                break;
            }
            start += 2;
        } else if (length == 127) {
            if (total - start < 8) {
                break;
            }
            uint64_t wide = 0;
            for (int i = 0; i < 8; i++) {
                wide = wide << 8 | buffer[start + i];
            }
            if (wide < 65536 || wide > (uint64_t)PY_SSIZE_T_MAX) {
                break;
            }
            length = (Py_ssize_t)wide;
            start += 8;
        }

        if ((max_size >= 0 && length > max_size) || length > total - start) {
            break;
        }

        PyObject *item;
        if (first == 0x81) {
            item = PyUnicode_DecodeUTF8((const char *)buffer + start, length, NULL);
            if (item == NULL) {
                if (PyErr_ExceptionMatches(PyExc_UnicodeDecodeError)) {
                    PyErr_Clear();
                    break;
                }
                PyBuffer_Release(&view);
                return NULL;
            }
        } else {
            item = PyBytes_FromStringAndSize((const char *)buffer + start, length);
            if (item == NULL) {
                PyBuffer_Release(&view);
                return NULL;
            }
        }

        PyObject *appended = PyObject_CallMethodOneArg(messages, state->append_name, item);
        Py_DECREF(item);
        if (appended == NULL) {
            PyBuffer_Release(&view);
            return NULL;
        }
        Py_DECREF(appended);

        offset = start + length;
    }

    PyBuffer_Release(&view);
    return PyLong_FromSsize_t(offset);
}

static PyMethodDef methods[] = {
    {"frame", (PyCFunction)(void (*)(void))frame, METH_FASTCALL, frame_doc},
    {"parse", (PyCFunction)(void (*)(void))parse, METH_FASTCALL, parse_doc},
    {NULL, NULL, 0, NULL}
};

PyDoc_STRVAR(module_doc, "C helpers for fablecord.net.websocket, used when they could be built.");

static int websocket_exec(PyObject *module)
{
    websocket_state *state = (websocket_state *)PyModule_GetState(module);

    state->append_name = PyUnicode_InternFromString("append");
    return state->append_name == NULL ? -1 : 0;
}

static int websocket_traverse(PyObject *module, visitproc visit, void *arg)
{
    websocket_state *state = (websocket_state *)PyModule_GetState(module);

    Py_VISIT(state->append_name);
    return 0;
}

static int websocket_clear(PyObject *module)
{
    websocket_state *state = (websocket_state *)PyModule_GetState(module);

    Py_CLEAR(state->append_name);
    return 0;
}

static void websocket_free(void *module)
{
    websocket_clear((PyObject *)module);
}

static PyModuleDef_Slot slots[] = {
    {Py_mod_exec, websocket_exec},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {0, NULL}
};

static struct PyModuleDef module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "fablecord._speedups.websocket",
    .m_doc = module_doc,
    .m_size = sizeof(websocket_state),
    .m_methods = methods,
    .m_slots = slots,
    .m_traverse = websocket_traverse,
    .m_clear = websocket_clear,
    .m_free = websocket_free
};

PyMODINIT_FUNC PyInit_websocket(void)
{
    return PyModuleDef_Init(&module);
}