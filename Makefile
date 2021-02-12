.DEFAULT_GOAL := upload

#libs needed to upload to pypi:
# pip install twine wheel
upload:
	@echo "Build and publish to pypi"
	$(RM) -r ./dist/ ./build/
	@python3 setup.py sdist bdist_wheel
	@#python3 -m twine upload dist/*
	@python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# install:
# extra url is needed to look in the real pypi for dependencies which are not available include the "test" one
# such a package is flask-restful, which only exists in https://pypi.org/simple/
# 	python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ cst-micro-chassis

clean:
	@echo "Cleaning up . . ."
	$(RM) -r ./dist/ ./build/
	@echo "Cleanup finished."
