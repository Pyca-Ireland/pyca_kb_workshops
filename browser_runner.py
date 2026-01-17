import asyncio
from pprint import pprint
from browser_use import Agent, Browser, ChatBrowserUse


async def run_parallel_agents(topic: str) -> str:
    sites = [
        ("https://lu.ma/dublin", "luma"),
        ("https://www.meetup.com/find/?location=ie--Dublin", "meetup"),
        ("https://www.eventbrite.ie/d/ireland--dublin/events/", "eventbrite"),
    ]

    browsers = [
        Browser(
            user_data_dir=f'./temp-profile-{i}',
            headless=True,  # ⚠️ headless TRUE for server/slack
        )
        for i in range(len(sites))
    ]

    agents = [
        Agent(
            task=f"""
            The topic at hand is: {topic}
            It is possible that the topic may be a setence for instance "Find me xyz of abc" - You must be able to identify intent and use a proper
            pattern for searching.

            Goal: Is to find events (max 3 per instance/website you are accessing) - We are looking for the name of the event,
            the organisers, the address if applicble, the date and time range if applicble and also the URL of the said event

            RULESET: You may only click to focus further information on an event if you need to get its URL dont do it for all events you see,
            choose the top 3 most relevant ones to the topic at hand.

            1. Go to {url}
            NOTE: If the instance website is luma, you do not need to use the search feature, you may just scroll down - for the other
            instance websites you might need to search up.
            2. Locate the to 3 events that are relevant to the topic - sometimes the information may not be shown yet or may require to be clicked on to fuerther check it.
            3. Once collected the websites return in this format:
            Return in results ONLY markdown format syntax, they cannot be inlined and must follow seperated line for each point. 
            use #, for hierarchy etc. - Ensure you use MARKDOWN syntax.
            
            Name of event:
            Organiser:
            Date:
            Location:
            URL:     
            """,
            browser=browsers[i],
            llm=ChatBrowserUse(),
        )
        for i, (url, _) in enumerate(sites)
    ]

    results = await asyncio.gather(
        *[agent.run() for agent in agents], return_exceptions=True
    )

    output = []

    for (url, name), r in zip(sites, results):
        if not isinstance(r, Exception):
            text = str(r.final_result()).replace('\\n', '\n')
            output.append(f"*{name.upper()}*\n{text}")

    return "\n\n---\n\n".join(output)


def run_browseruse(topic: str) -> str:
    """Sync wrapper for Slack"""
    return asyncio.run(run_parallel_agents(topic))
