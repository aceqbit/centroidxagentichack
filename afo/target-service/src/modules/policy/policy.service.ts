import { Injectable } from '@nitrostack/core';

@Injectable()
export class PolicyService {
  private activePolicy = {
    redact_fields: ['zip_code'],
    group_adjustments: { 'income': 1.1 },
    rationale: 'Mitigating geographic bias detected in zip_code 10044.'
  };

  async getActive() {
    return this.activePolicy;
  }

  async getHistory() {
    return [
      {
        ...this.activePolicy,
        timestamp: new Date().toISOString()
      }
    ];
  }
}