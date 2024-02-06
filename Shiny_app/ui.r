ui <- dashboardPage(
  
  skin = "green",
  
  dashboardHeader(title = "Biosphere 2"),
  
  dashboardSidebar(
    
    sidebarMenu(
      menuItem("Live",tabName = "live_tab",icon = icon("leaf")),
      menuItem("Irrigation",tabName = "irr_tab",icon = icon("droplet")),
      menuItem("NDVI",tabName = "cam_tab",icon = icon("camera"))
      
    )
    
  ),
  
  dashboardBody(
    
    tabItems(
      
      tabItem(tabName = "live_tab",
              fluidPage(
                
                fluidRow(
                  dateInput("cameraDate", "Date:", value = Sys.Date())
                )
                
              )
      ),
      
      tabItem(tabName = "irr_tab",
              fluidPage(
                
                fluidRow(
                  dateInput("dateInputStart", "Start date:", value = Sys.Date()-10),
                  dateInput("dateInputEnd", "End date:", value = Sys.Date())
                ),
                
                fluidRow(
                  box(plotlyOutput("vwcplot", height = 500), title = "Daily Median Soil Moisture", width = 12, solidHeader = TRUE, height = "560px")
                ),
                
                fluidRow(
                  box(plotlyOutput("volumeplot", height = 500), title = "Daily Irrigation Volume Delivered", width = 12, solidHeader = TRUE, height = "560px"),
                )
                
              )
      ),
      
      tabItem(tabName = "cam_tab",
              fluidPage(
                
                fluidRow(
                  #box(plotlyOutput("JSGMicrometPlot", height = 300), title = "Air Temp and RH", width = 6, solidHeader = TRUE, height = "360px"),
                  #box(plotlyOutput("JSGPrecipPlot", height = 300), title = "Precipitation", width = 6, solidHeader = TRUE, height = "360px")
                )
                
              )
      )
      
      
    )
    
  )
  
)