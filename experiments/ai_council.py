from chatarena.agent import Player, Moderator
from chatarena.backends import OpenAIChat
from chatarena.backends.human import Human
from chatarena.arena import Arena
from chatarena.environments.conversation import ModeratedConversation, Conversation

MODEL = "gpt-4"


def main():
    # Describe the environment (which is shared by all players)
    environment_description = """
    This is a board of advisors that advices the CEO of a startup on a question that the CEO ask.
    The board of advisors is composed of six members with different expertise.
    1. Industry veteran in finance like Warren Buffet
    2. Industry veteran in business strategy like Jeff Bezos
    3. Industry veteran in marketing like Seth Godin
    4. Industry veteran in negotiation like Chris Voss
    5. Industry veteran in technology like Elon Musk
    The five board members have to discuss among them. They are free to disagree with each other, and suggest an alternative approach, until they reach consensus.
    Do not always agree with the CEO or the other advisors on the board.
    """

    ceo = Player(name="CEO", backend=Human(),
                 role_desc="You are CEO.",
                 # terminal_condition="Have the board of advisors reach consensus? Answer yes or no.",
                 global_prompt=environment_description)

    warrent_buffet = """Warren Buffet follows the Benjamin Graham school of value investing, which looks for securities whose prices are unjustifiably low based on their intrinsic worth. He has developed several core tenets to help him employ his investment philosophy to maximum effect. These tenets fall into four categories: business, management, financial measures, and value.

In terms of business tenets, Buffet restricts his investments to businesses he can easily analyze. In terms of management tenets, Buffet evaluates the track records of a company’s higher-ups to determine if they have historically reinvested profits back into the company or if they have redistributed funds to back shareholders in the form of dividends. In terms of financial measures, Buffet focuses on low-levered companies with high profit margins. Finally, in terms of value tenets, Buffet looks for companies with a special product and good profit margins."""
    player1 = Player(name="Finance Advisor", backend=OpenAIChat(model=MODEL),
                     role_desc=f"You are the finance advisor like Warrent Buffet. Here is a brief description of Warrent Buffet:\n {warrent_buffet}",
                     global_prompt=environment_description)

    jeff_bezos = """Jeff Bezos is known for his success as an investor and businessman. He manages his portfolio through the investment firm he founded, Bezos Expeditions, and currently holds positions in dozens of companies. Some of the important tips to invest like Jeff Bezos include building a diversified portfolio, being a long-term investor, and investing in modern, cutting-edge companies ². He also believes in finding opportunity in crisis and knowing what the crowd thinks. """
    player2 = Player(name="Business Strategist", backend=OpenAIChat(model=MODEL),
                     role_desc=f"You are the business strategist like Jeff Bezos. Here is a brief description of Jeff Bezos:\n {jeff_bezos}",
                     global_prompt=environment_description)

    seth_godin = """Seth Godin is a bestselling author and entrepreneur known for his insights on marketing. He advises entrepreneurs to build products worth shouting about, rather than shouting about their products from the rooftops. He recommends approaching marketing strategy with four key points of focus: Coordination, Trust, Permission, and the Exchange of Ideas. He also emphasizes the importance of spreading your idea, thinking out of the box, and making your customers obsessed with your product or service."""
    player3 = Player(name="Marketing Expert", backend=OpenAIChat(model=MODEL),
                     role_desc=f"You are the marketing expert like Seth Godin. Here is a brief description of Seth Godin:\n{seth_godin}",
                     global_prompt=environment_description)

    christ_voss = """Chris Voss is a former FBI lead hostage negotiator and a leading authority on the art of negotiation. He teaches communication skills and strategies to help people get more of what they want every day. Some of his key principles of negotiation include showing the other side that you are negotiating in good faith, being genuinely interested in what drives the other side, taking emotions into consideration, building trust-based influence through the use of tactical empathy, working to deactivate negative feelings, aiming to magnify positive emotions, and keeping an eye out for black swans."""
    player4 = Player(name="Negotiation Expert", backend=OpenAIChat(model=MODEL),
                     role_desc=f"You are the negotiation expert like Chris Voss. Here is a brief description of Chris Voss:\n{christ_voss}",
                     global_prompt=environment_description)

    elon_musk = """Elon Musk is a visionary entrepreneur known for his views on technology and its potential to change the world. He has long been convinced that for life to survive, humanity has to become a multiplanet species. He founded Space Exploration Technologies (SpaceX) in 2002 to make more affordable rockets. Musk has also been involved in efforts to revolutionize battery technology. However, he has also warned of the dangers of artificial intelligence and has ramped up efforts in this area."""
    player5 = Player(name="Technology Expert", backend=OpenAIChat(model=MODEL),
                     role_desc=f"You are the technology expert like Elon Musk. Here is a brief description of Elon Musk:\n{elon_musk}",
                     global_prompt=environment_description)

    conversation = Conversation(
        player_names=[p.name for p in [ceo, player1, player2, player3, player4, player5]],
        # moderator=moderator,
        parallel=False,
        moderator_visibility="all",
        moderator_period="round",
    )

    arena = Arena(
        environment=conversation,
        players=[ceo, player1, player2, player3, player4, player5],
        global_prompt=environment_description,
    )
    arena.launch_cli(max_steps=100, interactive=True)


if __name__ == "__main__":
    main()
