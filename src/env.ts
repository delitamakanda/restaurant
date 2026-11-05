export interface Env {
  /** Jeton attendu dans l'en-tête `Webhook-Token` (secret Wrangler). */
  WEBHOOK_TOKEN?: string;
  /** "true" pour refuser les écritures sur les routes json-server. */
  READ_ONLY?: string;
  /** Origines CORS autorisées, séparées par des virgules, ou "*". */
  CORS_ORIGINS?: string;
}
