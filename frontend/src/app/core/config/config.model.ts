export interface AppConfig {
  apiUrl: string;

  cognito: {
    authority: string;
    redirectUrl: string;
    clientId: string;
    scope: string;
    responseType: string;
    customParamsEndSessionRequest: {
      client_id: string;
      logout_uri: string;
    };
  };
}
