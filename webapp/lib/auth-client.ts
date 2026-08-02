import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
  // ponytail: jwtClient plugin types lag createAuthClient generics — runtime OK
  plugins: [jwtClient() as never],
});

export const { useSession } = authClient;
