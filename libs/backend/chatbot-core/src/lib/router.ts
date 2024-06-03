import { trpcServer } from "./context";
import axios from "axios";
import { z } from "zod";

export const appRouter = trpcServer.router({
    fetch_result: trpcServer.procedure
        .input(
            z.object({
                query: z.string(),
            }),
        )
        .query(async ({ input }): Promise<string> => {
            let result = "";
            try {
                const response = await axios.post("http://localhost:4444/answer", { query: input.query });
                console.log("successful Result:", response.data);
                result = response.data.result;
            } catch (error: any) {
                let errorMessage = error.message;
                if (axios.isAxiosError(error)) {
                    errorMessage = error.response?.data || error.message;
                }
                console.error("Error uploading docs to vector db:", errorMessage);
            }
            return result;
        }),
});

export type AppRouter = typeof appRouter;
