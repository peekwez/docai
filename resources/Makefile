STAGE:=dev
LOG_LEVEL:=INFO
ASSET_ROOT:=../src

ARGS:=--context stage=${STAGE} \
	--context asset_root=${ASSET_ROOT} \
	--context log_level=${LOG_LEVEL}

synth:
	$(info [+] Synthesizing resources...)
	cdk synth ${ARGS} --all

deploy: synth
	$(info [+] Deploying resources...)
	cdk deploy ${ARGS} --all

destroy:
	$(info [+] Destroying resources...)
	cdk destroy ${ARGS} --all


list:
	$(info [+] Listing resources...)
	cdk ls ${ARGS} --all
