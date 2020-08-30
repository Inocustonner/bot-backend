//event:
//	id
//	arbs:
//		[arb:]
//			id
//			[bets:]
//				bet:
//					bookmaker, outcome, koef, url

function getArb(arbetel, id)
{
    arb = {id : id, bets : []}
    for (let i = 0; i < arbetel.childElementCount - 1; ++i)
    {
        bet = 
        { 
            bookmaker : arbetel.querySelectorAll(".content.bookmakerLinkContainer")[i].innerText,
            outcome : arbetel.querySelectorAll(".content.text-center.compareLinkContainer>a")[i].title,
            koef : parseFloat(arbetel.querySelectorAll(".content.text-right.relative.outcomeKoef>a")[i].innerText),
            url : arbetel.querySelectorAll(".content.text-right.relative.outcomeKoef>a")[i].href
        };
        arb.bets.push(bet);
    }
    return arb;
}

function main()
{
    arbets = document.querySelectorAll(".col-xs-12.arb-item-body-js")
    if (!arbets) return;

    betsjson = {events: []}

    for (arbetel of arbets)
    {
        arb_event = arbetel.parentElement.className.match(/(?<=event_|arb_)(\w|\d)+/ig)
        inflag = false;
        for(event of betsjson.events)
        {
            if (arb_event[1] == event.id)
            {
                event.arbs.push(getArb(arbetel, arb_event[0]));
                inflag = true;
            }
        }
        if (!inflag)
        {
            betsjson.events.push({id : arb_event[1], arbs : []});
            betsjson.events[betsjson.events.length - 1].arbs.push(getArb(arbetel, arb_event[0]));
        }
    }
    if (betsjson.events.length) port.postMessage(betsjson);
}


function onloading()
{
    if (document.querySelector("#arbsScroll"))
    {
        loadingWaiter.disconnect();
        new MutationObserver(main).observe(document.querySelector("#arbsScroll"), { childList: true, subtree: true });
    } 
}

// on arbs update call main
console.log(document.querySelector("#arbsScroll"));
loadingWaiter = new MutationObserver(onloading);
loadingWaiter.observe(document.querySelector(".arbs"), { childList: true, subtree: true })

// create tunnel to background script
port = chrome.runtime.connect();