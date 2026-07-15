/**
 * Strips the /api prefix from incoming request URIs before
 * forwarding to the API Gateway origin.
 * @param {Object} event - CloudFront Function viewer-request event
 * @param {Object} event.request - The incoming request object
 * @param {string} event.request.uri - The request URI to rewrite
 * @returns {Object} The modified request object
 */
function handler(event) {
  const request = event.request;
  request.uri = request.uri.replace(/^\/api/, "");

  return request;
}
