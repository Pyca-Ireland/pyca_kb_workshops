import asyncio

from browser_use import Agent, Browser, ChatBrowserUse


SITES = [
    ("https://lu.ma/dublin", "luma"),
    ("https://www.meetup.com/find/?location=ie--Dublin", "meetup"),
    ("https://www.eventbrite.ie/d/ireland--dublin/events/", "eventbrite"),
]


async def search_events(topic: str) -> str:
    """Search for events across multiple sites based on the given topic."""

    browsers = [
        Browser(
            user_data_dir=f'./temp-profile-{i}',
            headless=True,
        )
        for i in range(len(SITES))
    ]

    agents = [
        Agent(
            task=f"""
            The topic at hand is: {topic}
            It is possible that the topic may be a sentence for instance "Find me xyz of abc" - You must be able to identify intent and use a proper
            pattern for searching.

            Goal: Is to find events (max 3 per instance/website you are accessing) - We are looking for the name of the event,
            the organisers, the address if applicable, the date and time range if applicable and also the URL of the said event

            RULESET: You may only click to focus further information on an event if you need to get its URL dont do it for all events you see,
            choose the top 3 most relevant ones to the topic at hand.

            1. Go to {url}
            NOTE: If the instance website is luma, you do not need to use the search feature, you may just scroll down - for the other
            instance websites you might need to search up.
            2. Locate the top 3 events that are relevant to the topic - sometimes the information may not be shown yet or may require to be clicked on to further check it.
            3. Once collected the websites return in this format:

            Return in results ONLY markdown format syntax, they cannot be inlined and must follow separated line for each point.
            use #, for hierarchy etc. - Ensure you use MARKDOWN syntax.

            Format must be this, and ONLY THIS. Do not return anything else for instance: Incorrect format - "I could only find two results.." etc, 
            Return this EXACT format. 

            # Event 1 : [Title]
            **Organiser** : [Organiser]
            **Date** : [Date]
            **Location** : [Location]
            *URL:* [URL] 

            If one of the [] such as organiser isnt available, just put N/A 
            Do not use seperator lines at ALL
            If you cant find a 3rd event, just dont include it at all in the MD output. 

            Name of event:
            Organiser:
            Date:
            Location:
            URL:
            """,
            browser=browsers[i],
            llm=ChatBrowserUse(),
        )
        for i, (url, name) in enumerate(SITES)
    ]

    results = await asyncio.gather(
        *[agent.run() for agent in agents], return_exceptions=True
    )

    # Build markdown output
    output = []
    for (url, name), r in zip(SITES, results):
        if not isinstance(r, Exception):
            text = str(r.final_result()).replace('\\n', '\n')
            output.append(f"# {name.upper()}\n\n{text}\n\n---\n")

    return '\n'.join(output)


if __name__ == "__main__":
    # CLI usage
    topic = "tech events"
    result = asyncio.run(search_events(topic))
    print(result)
