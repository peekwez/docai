STAGE:=Dev

invoke: invoke-create-schema

invoke-create-schema:
	sam local invoke \
		CreateSchemaLambda \
		--event ./create_schema/event.json \
		-t ../../resources/cdk.out/DocumentAIStack${STAGE}.template.json
