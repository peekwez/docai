import { SSM } from "@aws-sdk/client-ssm";
import { SecretsManager } from "@aws-sdk/client-secrets-manager";

class Config {
  #ssm;
  #secret;

  constructor() {
    const region = process.env.AWS_REGION || "ca-central-1";
    this.#ssm = new SSM({ region });
    this.#secret = new SecretsManager({ region });
  }

  async getParameter(name) {
    const { Parameter: parameter } = await this.#ssm.getParameter({
      Name: name,
    });
    return parameter;
  }

  async getSecretValue(name) {
    const { Value: SecretId } = await this.getParameter(name);
    const { SecretString: secretValue } = await this.#secret.getSecretValue({
      SecretId,
    });
    return secretValue;
  }
}

export { Config };
