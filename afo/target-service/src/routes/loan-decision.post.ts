import { LoanDecisionTool } from '../modules/loan-decision/evaluate_loan.tool';

const loanTool = new LoanDecisionTool();

export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const result = await loanTool.evaluateLoanApplication(body);
  return result;
});