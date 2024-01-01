deploy: deploy.resources

destroy: destroy.resources

invoke: invoke.create-schema

deploy.resources:
	$(info [+] Deploying resources...)
	$(MAKE) -C resources/ deploy


destroy.resources:
	$(info [+] Destroying resources...)
	$(MAKE) -C resources/ destroy


invoke.create-schema:
	$(info [+] Testing create-schema...)
	$(MAKE) -C src/functions/ invoke-create-schema
