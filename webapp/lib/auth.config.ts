import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { APIError } from "better-auth/api";
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export const authConfig = {
  database: pool,
  emailAndPassword: {
    enabled: true,
  },
  plugins: [jwt()],
  databaseHooks: {
    user: {
      create: {
        before: async () => {
          const result = await pool.query<{ count: string }>(
            'SELECT count(*)::text AS count FROM "user"',
          );
          const count = Number.parseInt(result.rows[0]?.count ?? "0", 10);
          if (count > 0) {
            throw new APIError("CONFLICT", {
              message: "SIGNUP_LOCKED",
            });
          }
        },
      },
    },
  },
} as const;

export const auth = betterAuth(authConfig);
