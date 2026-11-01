// Working registration example: real model calendar report, no placeholder economics.
registerWorkerRouteModule({version:1,id:'example-calendar',operations:{summary:{mode:'preview',fields:{},execute(payload,ctx){const calendar=civicCalendarView();ctx.notify('Calendar review prepared for day '+G.day+'.');return {day:G.day,calendar};}}}});
