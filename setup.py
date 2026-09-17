from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            name="fablecord._speedups.websocket",
            sources=["src/fablecord/_speedups/websocket.c"],
            optional=True
        )
    ]
)