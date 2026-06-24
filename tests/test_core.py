import pytest
from axentx_product import Brain, Agent

def test_brain_store_retrieve():
    brain = Brain()
    brain.store("product_idea", "AI toothbrush")
    assert brain.retrieve("product_idea") == "AI toothbrush"

def test_brain_search():
    brain = Brain()
    brain.store("market_demand", "People want faster horses")
    brain.store("tech_stack", "Python, Rust")
    
    results = brain.search("python")
    assert "tech_stack" in results
    
    results = brain.search("horses")
    assert "market_demand" in results

def test_agent_execution():
    brain = Brain()
    agent = Agent("Scout", brain)
    
    msg = agent.execute("Find market signals")
    assert "Scout processed" in msg
    assert brain.retrieve("log_Scout") == msg
