import nox


@nox.session
@nox.parametrize(
    "python, django",
    [(python, django) for python in ("3.9", "3.10", "3.11", "3.12") for django in ("3.2", "4.0", "4.1", "4.2", "5.0", "5.2")],
)
def tests(session, django):
    session.run("poetry", "install", external=True)
    session.install(f"django=={django}")
    session.run("pytest", "--cov", "--cov-report=xml")


lint_dirs = ["django_credentials", "env_credentials"]


@nox.session(python=["3.9"])
def types(session):
    session.run("poetry", "install", external=True)
    session.run("mypy", ".", external=True)


@nox.session(python=["3.9"])
def formatting(session):
    session.run("poetry", "install", external=True)
    session.run("flake8", *lint_dirs)
    session.run("isort", "--check-only", "--diff", "--force-single-line-imports", "--profile", "black", *lint_dirs)
    session.run("black", "--check", "--diff", *lint_dirs)
