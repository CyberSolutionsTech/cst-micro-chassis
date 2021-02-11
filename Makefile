all : test upload clean
.PHONY: all

upload:
	@echo "Build and publish to pypi"
	@python3 setup.py sdist bdist_wheel
	@python3 -m twine upload dist/*
#	@python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# install:
# 	@python3 -m pip install --index-url https://test.pypi.org/simple/ subscribear

clean:
	@echo "Cleaning up . . ."
	$(rm) -r ./dist/
	$(rm) -r ./build/
	@echo "Cleanup finished."
