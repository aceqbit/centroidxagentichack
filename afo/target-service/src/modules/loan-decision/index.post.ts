export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  // Placeholder: loan-decision module will be implemented here
  return {
    module: 'loan-decision',
    received: body,
    decision: null,
    message: 'Module not yet implemented',
  }
})
