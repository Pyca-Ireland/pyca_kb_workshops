import asyncio
from pprint import pprint

from browser_use import Agent, Browser, ChatBrowserUse


async def run_parallel_agents() -> None:
    topic = "tech events or give(a)go events"

    # Define different meetup websites to scrape
    sites = [
        ("https://lu.ma/dublin", "luma"),
        ("https://www.meetup.com/find/?location=ie--Dublin", "meetup"),
        ("https://www.eventbrite.ie/d/ireland--dublin/events/", "eventbrite"),
    ]

    # Create separate browser instances for isolation
    browsers = [
        Browser(
            user_data_dir=f'./temp-profile-{i}',
            headless=False,
        )
        for i in range(len(sites))
    ]

    # Create agents for each site
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
        for i, (url, name) in enumerate(sites)
    ]

    # Run all agents in parallel
    results = await asyncio.gather(
        *[agent.run() for agent in agents], return_exceptions=True
    )

    pprint(results)

    with open('results.md', 'w') as f:
        for (url, name), r in zip(sites, results):
            if not isinstance(r, Exception):
                text = str(r.final_result()).replace('\\n', '\n')
                f.write(f"# {name.upper()}\n\n{text}\n\n---\n\n")


asyncio.run(run_parallel_agents())
