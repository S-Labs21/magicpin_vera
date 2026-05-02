import uuid
import os
from typing import Dict, Any, Optional

def compose(category: Dict[str, Any], merchant: Dict[str, Any], trigger: Dict[str, Any], customer: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Composes a message based on the trigger type, merchant context, and category guidelines.
    Returns: { body, cta, send_as, suppression_key, rationale, template_name, template_params }
    """
    kind = trigger.get("kind", "")
    trigger_id = trigger.get("trigger_id", f"trg_{uuid.uuid4().hex[:8]}")
    payload = trigger.get("payload", {})
    
    merchant_name = merchant.get("identity", {}).get("name", "Merchant")
    
    # Defaults
    send_as = "vera"
    body = f"Hi {merchant_name}, I am Vera, your magicpin assistant."
    cta = "none"
    suppression_key = f"{trigger_id}_{merchant.get('merchant_id')}"
    rationale = f"Handled trigger of kind: {kind}"
    template_name = "default_template"
    template_params = []

    # Helper functions
    def get_active_offer():
        offers = merchant.get("offers", {}).get("active", [])
        if offers:
            return offers[0].get("title", offers[0].get("name", "a special offer"))
        return "a special offer"

    # Strategy Implementation
    if kind in ["research_digest", "category_research_digest_release"]:
        digest_item = category.get("research_digest", [])
        title = digest_item[0].get("title", "new trend") if digest_item else "a recent insight"
        body = f"Hi {merchant_name}, I noticed a '{title}' trend in your category. Want me to draft a quick WhatsApp campaign for your customers based on this?"
        cta = "Want me to draft a customer WhatsApp from this?"
        rationale = "Used category digest item to suggest a campaign."
        template_name = "research_digest_v1"
        template_params = [merchant_name, title]
        
    elif kind == "perf_spike":
        delta = payload.get("delta", merchant.get("performance", {}).get("views", {}).get("delta_7d", "a spike"))
        body = f"Great news {merchant_name}! Your profile saw a {delta} spike in views recently. Want me to turn this momentum into a quick campaign?"
        cta = "Want me to turn this into a quick campaign?"
        rationale = "Mentioned performance spike and suggested campaign."
        template_name = "perf_spike_v1"
        template_params = [merchant_name, str(delta)]
        
    elif kind == "perf_dip":
        delta = payload.get("drop", merchant.get("performance", {}).get("views", {}).get("delta_7d", "a drop"))
        body = f"Hi {merchant_name}, views are slightly down ({delta}) this week. Want me to draft a quick recovery post to get customers back?"
        cta = "Want me to draft a recovery post?"
        rationale = "Mentioned performance dip and suggested recovery action."
        template_name = "perf_dip_v1"
        template_params = [merchant_name, str(delta)]
        
    elif kind == "stale_posts":
        stale_age = payload.get("age", "a few weeks")
        offer = get_active_offer()
        body = f"Hi {merchant_name}, your last post was {stale_age} ago. Should I draft a new post featuring your '{offer}' to keep your profile fresh?"
        cta = "Should I draft it?"
        rationale = "Addressed stale posts by offering to feature an active offer."
        template_name = "stale_posts_v1"
        template_params = [merchant_name, str(stale_age), offer]

    elif kind == "ctr_below_peer_median":
        my_ctr = payload.get("merchant_ctr", "current")
        peer_ctr = payload.get("peer_median_ctr", "average")
        body = f"Hi {merchant_name}, your CTR is {my_ctr} compared to the peer average of {peer_ctr}. Want me to rewrite your profile offer to attract more clicks?"
        cta = "Want me to rewrite your profile offer?"
        rationale = "Compared CTR and suggested profile improvement."
        template_name = "ctr_below_peer_v1"
        template_params = [merchant_name, str(my_ctr), str(peer_ctr)]

    elif kind == "festival_upcoming":
        festival = payload.get("festival", "upcoming festival")
        body = f"Hi {merchant_name}, {festival} is coming up! Reply YES and I’ll draft a special festival message for your customers."
        cta = "Reply YES and I’ll draft the festival message."
        rationale = "Suggested a festival campaign."
        template_name = "festival_v1"
        template_params = [merchant_name, festival]

    elif kind == "weather_heatwave" or kind == "local_event":
        event = payload.get("event", "heatwave")
        body = f"Hi {merchant_name}, there's a {event} expected. I can create a quick context-specific reminder for your customers. Want a 2-line customer WhatsApp?"
        cta = "Want a 2-line customer WhatsApp?"
        rationale = "Suggested context-specific message based on weather/event."
        template_name = "weather_v1"
        template_params = [merchant_name, event]

    elif kind in ["recall_due", "customer_lapsed_soft"] and customer:
        send_as = "merchant_on_behalf"
        cust_name = customer.get("name", "there")
        last_visit = customer.get("last_visit", "recently")
        offer = get_active_offer()
        body = f"Hi {cust_name}, it's been a while since your visit on {last_visit}. We have {offer} running! Reply YES to book your next slot."
        cta = "Reply YES to book."
        rationale = "Drafted soft recall message using customer details and active offer."
        template_name = "recall_due_v1"
        template_params = [cust_name, last_visit, offer]
        suppression_key = f"{trigger_id}_{merchant.get('merchant_id')}_{customer.get('customer_id')}"

    elif kind == "appointment_tomorrow" and customer:
        send_as = "merchant_on_behalf"
        cust_name = customer.get("name", "there")
        appt_time = payload.get("appointment_time", "tomorrow")
        body = f"Hi {cust_name}, gentle reminder for your appointment at {merchant_name} {appt_time}. Reply C to confirm or R to reschedule."
        cta = "Reply C to confirm or R to reschedule."
        rationale = "Sent appointment reminder."
        template_name = "appt_tomorrow_v1"
        template_params = [cust_name, merchant_name, appt_time]
        suppression_key = f"{trigger_id}_{merchant.get('merchant_id')}_{customer.get('customer_id')}"

    elif kind == "review_theme_emerged":
        theme = payload.get("theme", "recent feedback")
        body = f"Hi {merchant_name}, I noticed a theme in your recent reviews regarding '{theme}'. Want me to draft a standardized reply or a quick action plan?"
        cta = "Want me to draft the reply?"
        rationale = "Addressed review theme."
        template_name = "review_theme_v1"
        template_params = [merchant_name, theme]

    elif kind == "dormant_with_vera":
        body = f"Hi {merchant_name}, it's been a quiet week. I have a quick idea to boost your engagement. Want one quick idea for this week?"
        cta = "Want one quick idea for this week?"
        rationale = "Soft reactivation for dormant merchant."
        template_name = "dormant_v1"
        template_params = [merchant_name]

    elif kind == "competitor_opened":
        comp_name = payload.get("competitor_name", "A new competitor")
        dist = payload.get("distance", "nearby")
        body = f"Hi {merchant_name}, {comp_name} recently opened {dist} from you. Want me to prepare a quick counter-offer campaign to retain your loyal customers?"
        cta = "Want me to prepare a quick counter-offer?"
        rationale = "Competitor alert and counter-strategy."
        template_name = "competitor_v1"
        template_params = [merchant_name, comp_name, dist]

    elif kind == "category_trend_movement":
        trend = payload.get("trend", category.get("trend_signals", [{}])[0].get("name", "a new trend"))
        body = f"Hi {merchant_name}, searches for '{trend}' are moving up in your area. Want me to turn this trend into a post?"
        cta = "Want me to turn this trend into a post?"
        rationale = "Trend movement alert."
        template_name = "trend_v1"
        template_params = [merchant_name, trend]

    elif kind == "regulation_change":
        reg = payload.get("details", "a recent compliance update")
        body = f"Hi {merchant_name}, please note: {reg}. Want me to summarize what changes for your business?"
        cta = "Want me to summarize what changes for your clinic/store?"
        rationale = "Regulation change notification."
        template_name = "regulation_v1"
        template_params = [merchant_name, reg]

    elif kind == "milestone_reached":
        milestone = payload.get("milestone", "a new milestone")
        body = f"Congratulations {merchant_name}! You just reached {milestone}. Want me to draft a thank-you post for your customers?"
        cta = "Want me to draft a thank-you post?"
        rationale = "Milestone celebration."
        template_name = "milestone_v1"
        template_params = [merchant_name, milestone]
    else:
        # Generic fallback
        body = f"Hi {merchant_name}, checking in to help you manage your business on magicpin. How can I assist today?"
        cta = "open_ended"
        rationale = f"Fallback for unrecognized trigger kind: {kind}"

    # Optional LLM Enhancement can be added here if needed,
    # but rule-based ensures deterministic output and speed.

    return {
        "body": body,
        "cta": cta,
        "send_as": send_as,
        "suppression_key": suppression_key,
        "rationale": rationale,
        "template_name": template_name,
        "template_params": template_params
    }

