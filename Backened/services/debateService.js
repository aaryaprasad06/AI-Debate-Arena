const OpenAI = require("openai");

const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

async function generateProArgument(topic) {

    const response = await client.chat.completions.create({
        model: "gpt-4o-mini",

        messages: [
            {
                role: "system",
                content:
                    "You are an expert debater supporting the topic."
            },
            {
                role: "user",
                content: topic
            }
        ]
    });

    return response.choices[0].message.content;
}