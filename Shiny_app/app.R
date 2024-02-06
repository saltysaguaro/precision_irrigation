# B2 Precision Irrigation Shiny App
library(shiny)
library(shinythemes)
library(shinydashboard)
library(tidyverse)
library(plotly)
library(lubridate)

setwd("C:/Users/Kai Lepley/Box/School/RPi Precision Irrigation/precision_shiny/B2PrecisionIrrigation")

source("ui.R")
source("server.R")

shinyApp(ui, server)