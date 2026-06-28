export interface AppConfig {
  apiUrl: string;

  cognito: {
    authority: string;
    redirectUrl: string;
    clientId: string;
    scope: string;
    responseType: string;
    postLogoutRedirectUri: string;
  };
}
