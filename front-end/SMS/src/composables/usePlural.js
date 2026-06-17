/**
 * Returns "1 record" or "5 records" with proper singular/plural form.
 */
export const plural = (count, singular, pluralForm = null) => {
  const n = Number(count) || 0
  const pl = pluralForm || `${singular}s`
  return `${n} ${n === 1 ? singular : pl}`
}
