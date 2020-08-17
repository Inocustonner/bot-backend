const SERVERADDR = "http://192.168.6.3/api/send_info";
var bets_buffer = {};
MIN_WAIT = 6;

function remember_for(event_arb_id, min)
{
    bets_buffer[event_arb_id] = true;
    setTimeout( () => { delete bets_buffer[event_arb_id]; }, min * 60 * 1000);
}

function is_remembered(event_arb_id)
{
    return bets_buffer[event_arb_id];
}

chrome.runtime.onConnect.addListener(port =>
{
    port.onMessage.addListener(msg =>
    {
        for (event of msg.events)
        {
            event.arbs = event.arbs.filter(arb => !is_remembered(event.id + arb.id));// remove known forks
            event.arbs.forEach(arb => remember_for(event.id + arb.id, MIN_WAIT));// remember for 5 min
        }

        msg.events = msg.events.filter(e => e.arbs.length > 0);
        if (msg.events.length > 0)
        {
            r = new XMLHttpRequest();
            r.open("POST", SERVERADDR, true);
            r.setRequestHeader("Content-type", "application/json");
            r.send(JSON.stringify(msg));
        }
    })
});