const SERVERADDR = "http://192.168.6.3/api/send_info";

chrome.runtime.onConnect.addListener(port =>
{
    port.onMessage.addListener(msg =>
    {
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
