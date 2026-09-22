from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            name="fablecord._speedups.websocket",
            sources=["src/fablecord/_speedups/websocket.cpp"],
            optional=True
        ),
        Extension(
            name="fablecord._speedups.gateway",
            sources=["src/fablecord/_speedups/gateway.cpp"],
            optional=True
        ),
        Extension(
            name="fablecord._speedups.emoji",
            sources=["src/fablecord/_speedups/emoji.cpp"],
            optional=True
        )
    ]
)