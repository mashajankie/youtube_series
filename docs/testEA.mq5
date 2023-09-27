// Define input parameters
input int FastMA_Period = 10;       // Period for the fast moving average
input int SlowMA_Period = 20;       // Period for the slow moving average
input ENUM_TIMEFRAMES TimeFrame = PERIOD_H1; // Chart time frame
input double TakeProfit = 50;       // Take profit in points
input double StopLoss = 30;         // Stop loss in points

double FastMA[];
double SlowMA[];

int fast_handle;
int slow_handle;

int OnInit()
{
   // ArraySetAsSeries sets the indexing order for an array.
   ArraySetAsSeries(FastMA, true);
   ArraySetAsSeries(SlowMA, true);

   // Calculate moving averages initially
   fast_handle = iMA(_Symbol, TimeFrame, FastMA_Period, 0, MODE_SMA, PRICE_CLOSE);
   slow_handle = iMA(_Symbol, TimeFrame, SlowMA_Period, 0, MODE_SMA, PRICE_CLOSE);

   return(INIT_SUCCEEDED);
}

void OnTick()
{

   double Ask, Bid;
   SymbolInfoDouble(_Symbol, SYMBOL_ASK, Ask);
   SymbolInfoDouble(_Symbol, SYMBOL_BID, Bid);

   // Update moving averages
   CopyBuffer(fast_handle, 0, 0, 3, FastMA);
   CopyBuffer(slow_handle, 0, 0, 3, SlowMA);

   double currentFastMA = FastMA[0];
   double previousFastMA = FastMA[1];
   
   double currentSlowMA = SlowMA[0];
   double previousSlowMA = SlowMA[1];

   // Check if there's an existing order
   if(OrdersTotal() > 0)
      return;

   // Buy condition
   if(previousFastMA < previousSlowMA && currentFastMA > currentSlowMA)
   {
      double sl = NormalizeDouble(Ask - StopLoss*Point, Digits);
      double tp = NormalizeDouble(Ask + TakeProfit*Point, Digits);
      MqlTradeRequest request;
      MqlTradeResult  result;
      
      ZeroMemory(request);
      
      request.action   = TRADE_ACTION_DEAL;  // Immediate execution
      request.symbol   = _Symbol;
      request.volume   = 1.0;  // Volume of the order
      request.type     = ORDER_TYPE_BUY;
      request.price    = Ask;
      request.sl       = sl;
      request.tp       = tp;
      request.deviation= 2;
      request.comment  = "MA Crossover Buy";
      request.type_filling = ORDER_FILLING_FOK;
      
      if(!OrderSend(request, result))
         Print(StringFormat("OrderSend failed with error: %d", GetLastError()));
    }

   // Sell condition
   if(previousFastMA > previousSlowMA && currentFastMA < currentSlowMA)
   {
      double sl = NormalizeDouble(Bid + StopLoss*Point, Digits);
      double tp = NormalizeDouble(Bid - TakeProfit*Point, Digits);
      MqlTradeRequest request;
      MqlTradeResult  result;
      
      ZeroMemory(request);
      
      request.action   = TRADE_ACTION_DEAL;  // Immediate execution
      request.symbol   = _Symbol;
      request.volume   = 1.0;  // Volume of the order
      request.type     = ORDER_TYPE_SELL;
      request.price    = Bid;
      request.sl       = sl;
      request.tp       = tp;
      request.deviation= 2;
      request.comment  = "MA Crossover Sell";
      request.type_filling = ORDER_FILLING_FOK;
      
      if(!OrderSend(request, result))
         Print(StringFormat("OrderSend failed with error: %d", GetLastError()));
   
   }

}

void OnDeinit(const int reason)
{
   // Cleanup if necessary
}
