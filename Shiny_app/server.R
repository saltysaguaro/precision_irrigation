server <- function(input, output, session) { 
  
  ### Live view Raspberry Pi Camera input
  #img_lis <- list.files("https://agrivoltaicatlas.com/winter2022/")
  
  ### Precision Irrigation Analysis and Plotting
  # Import data
  pre_dat <- read.csv("https://agrivoltaicatlas.com/summer2023/precision/data_irrigation.txt", row.names = NULL, stringsAsFactors = F)
  if (length(pre_dat) == 11){
    print(length(pre_dat))
    pre_dat[, 10] <- paste0(pre_dat[, 10], pre_dat[, 11])
    pre_dat <- pre_dat[, 1:10]
    #colnames(pre_dat) <- c(colnames(pre_dat)[2:11], "Extra")
  }
  pre_dat <- pre_dat[pre_dat$Comment != "", ]
  pre_dat$Datetime <- as.POSIXct(pre_dat$Date)
  pre_dat$Date <- as.Date(pre_dat$Date)
  pre_dat[pre_dat == 0] <- NA
  
  # Gather data into long format
  real_long <- pre_dat %>% gather(Sensor, VWC, 3:6)
  
  pre_day <- pre_dat %>%
    mutate(Date = floor_date(Date)) %>%
    group_by(Date, Treatment) %>%
    summarize(AVLO = mean(AVLO), AVHI = mean(AVHI), CNLO = mean(CNLO), CNHI = mean(CNHI), Volume = sum(Volume, na.rm = T))
  pre_day <- pre_day[pre_day$Treatment != "none", ]
  pre_day_long <- pre_day %>% gather(Sensor, VWC, 3:6)
  
  pre_day_sens <- pre_dat %>%
    mutate(Date = floor_date(Date)) %>%
    group_by(Date) %>%
    summarize(AVLO = mean(AVLO, na.rm=T), AVHI = mean(AVHI, na.rm=T), CNLO = mean(CNLO, na.rm=T), CNHI = mean(CNHI, na.rm=T), Volume = sum(Volume, na.rm = T))
  
  pre_mer <- merge(pre_day, pre_day_sens, by=1)
  pre_mer <- pre_mer[, c(1, 2, 7, 8, 9, 10, 11)]
  colnames(pre_mer) <- c("Date", "Treatment", "Volume", "AVLO", "AVHI", "CNLO", "CNHI")
  pre_mer$Date <- as.Date(pre_mer$Date)
  pre_mer$Volume <- round(pre_mer$Volume, digits = 0)
  pre_mer$AVHI <- round(pre_mer$AVHI, digits = 2)
  pre_mer$AVLO <- round(pre_mer$AVLO, digits = 2)
  pre_mer$CNHI <- round(pre_mer$CNHI, digits = 2)
  pre_mer$CNLO <- round(pre_mer$CNLO, digits = 2)
  
  # Color palette
  treat_col <- c("#018571", "#80cdc1", "#a6611a", "#dfc27d")
  treat_nam <- c("Agrivoltaic High", "Agrivoltaic Low", "Control High", "Control Low")
  
  output$vwcplot <- renderPlotly({
    pre_mer_g <- subset(pre_mer, Date>=as.Date(input$dateInputStart) & Date<=as.Date(input$dateInputEnd))
    g1 <- ggplot(pre_mer_g, aes(x = Date)) +
      geom_line(aes(y = AVHI, color = "Agrivoltaic High")) +
      geom_line(aes(y = AVLO, color = "Agrivoltaic Low")) +
      geom_line(aes(y = CNHI, color = "Control High")) +
      geom_line(aes(y = CNLO, color = "Control Low")) +
      geom_hline(yintercept=0.25, linetype="dashed", color = "black") +
      geom_hline(yintercept=0.15, linetype="dashed", color = "gray") +
      #ylim(0, NA) +
      scale_color_manual(limits = treat_nam, values = treat_col) +
      xlab("Date") + ylab("Volumetric Water Content") + labs(color = "Treatment") +
      scale_x_date(breaks = pre_mer_g$Date, date_labels="%b %d") +
      theme_bw() +
      theme(axis.title = element_blank())
    ggplotly(g1)
  })
  
  output$volumeplot <- renderPlotly({
    pre_mer_g <- subset(pre_mer, Date>=as.Date(input$dateInputStart) & Date<=as.Date(input$dateInputEnd))
    g2 <- ggplot(pre_mer_g, aes(x=Date, y=Volume, fill=Treatment)) +
      geom_bar(stat="identity") +
      scale_fill_manual(limits = treat_nam, values = treat_col) +
      xlab("Date") + ylab("Irrigation Volume (Gallons)") +
      scale_x_date(breaks = pre_mer_g$Date, date_labels="%b %d") +
      theme_bw() +
      theme(axis.title = element_blank())
    ggplotly(g2)
  })
  
}