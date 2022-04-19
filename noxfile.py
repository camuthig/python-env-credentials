import nox


@nox.session(python=["3.6", "3.7", "3.8"])
@nox.parametrize("django", ["2.2", "3.0"])
def tests(session, django):
    session.run("poetry", "install", external=True)
    session.install(f"django=={django}")
    session.run("pytest", "--cov", "--cov-report=xml")


lint_dirs = ["django_credentials", "env_credentials"]


@nox.session(python=["3.8"])
def types(session):
    session.run("poetry", "install", external=True)
    session.run("mypy", ".", external=True)


@nox.session(python=["3.8"])
def formatting(session):
    session.run("poetry", "install", external=True)
    session.run("flake8", *lint_dirs)