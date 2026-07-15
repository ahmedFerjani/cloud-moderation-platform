/**
 * Rewrites extensionless paths to /index.html, enabling Angular
 * client-side routing for direct loads and refreshes.
 * @param {Object} event - CloudFront Function viewer-request event
 * @param {Object} event.request - The incoming request object
 * @param {string} event.request.uri - The request URI to rewrite
 * @returns {Object} The modified request object
 */
function handler(event) {
  const request = event.request;
  const uri = request.uri;

  if (!uri.includes(".")) {
    request.uri = "/index.html";
  }

  return request;
}
