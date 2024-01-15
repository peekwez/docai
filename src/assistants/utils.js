import AWS from "aws-sdk";

const AWS_REGION = "ca-central-1";
AWS.config.update({ region: AWS_REGION });

class Config {
  #ssm;
  #secret;

  constructor() {
    this.#ssm = new AWS.SSM();
    this.#secret = new AWS.SecretsManager();
  }

  async getParameter(name) {
    const { Parameter: parameter } = await this.#ssm
      .getParameter({ Name: name })
      .promise();
    return parameter;
  }

  async getSecretValue(name) {
    const { Value: SecretId } = await this.getParameter(name);
    const { SecretString: secretValue } = await this.#secret
      .getSecretValue({ SecretId })
      .promise();
    return secretValue;
  }
}

export { Config };
