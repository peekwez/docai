# import cdk
# from aws_cdk import aws_events as events


# class EventsStack(cdk.NestedStack):
#     def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
#         super().__init__(scope, id, **kwargs)
#         self.stage = self.node.try_get_context("stage")

#         # Rule for triggering the document processing
#         self.trigger_rule = events.Rule(
#             self,
#             "DocumentProcessingRule",
#             schedule=events.Schedule.rate(cdk.Duration.minutes(1)),
#         )

#         self.trigger_rule_param = ssm.StringParameter(
#             self,
#             "DocumentProcessingRuleName",
#             parameter_name=f"/{self.stage}/rule/document_processing_rule_name",
#             string_value=self.trigger_rule.rule_name,
#         )

#         self.trigger_rule_arn = self.trigger_rule.rule_arn
#         self.trigger_rule_param_arn = self.trigger_rule_param.parameter_arn
#         self.trigger_rule_param_name = self.trigger_rule_param.parameter_name

#     def add_access_to_trigger_rule(
#         self, fn: _lambda.Function, role: iam.Role, actions=list[str]
#     ):
#         fn.add_environment(
#             "TRIGGER_RULE_PARAMETER_NAME", self.trigger_rule_param.parameter_name
#         )
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=actions,
#                 resources=[self.trigger_rule.rule_arn],
#             )
#         )
#         role.add_to_policy(
#             iam.PolicyStatement(
#                 effect=iam.Effect.ALLOW,
#                 actions=["ssm:GetParameter"],
#                 resources=[self.trigger_rule_param.parameter_arn],
#             )
#         )

#     def add_trigger_rule_as_event_source(self, fn: _lambda.Function):
#         fn.add_event_source(
#             lambda_event_sources.EventBridgeRuleTarget(
#                 self.trigger_rule,
#             )
#         )
