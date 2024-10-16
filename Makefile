lint:
	ruff check ai_stream/
	mypy ai_stream/
	ruff format ai_stream/ --check

coverage:
	pytest --cov --cov-report term-missing tests/
