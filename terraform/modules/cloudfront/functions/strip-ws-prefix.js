/**
 * Strips the /ws prefix from incoming request URIs before
 * forwarding to the WebSocket API Gateway origin
 * NOTE: "$default" is hardcoded because CloudFront Functions
 * cannot rewrite the URI to an empty path. Update this value
 * if the WebSocket API stage name changes.
 * @param {Object} event - CloudFront Function viewer-request event
 * @param {Object} event.request - The incoming request object
 * @param {string} event.request.uri - The request URI to rewrite
 * @returns {Object} The modified request object
 */
function handler(event) {
  const request = event.request;
  request.uri = request.uri.replace(/^\/ws/, "/$default");

  return request;
}
