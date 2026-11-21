module uart_loopback #(parameter CLKS_PER_BIT = 868) (
    input  wire       clk,
    input  wire       rst,
    input  wire       tx_start,
    input  wire [7:0] tx_data,
    output wire       tx_busy,
    output wire [7:0] rx_data,
    output wire       rx_valid,
    output wire       frame_error
);
    wire serial;   // the wire connecting TX to RX

    // Transmitter: sends tx_data out onto the serial wire
    uart_tx #(.CLKS_PER_BIT(CLKS_PER_BIT)) u_tx (
        .clk      (clk),
        .rst      (rst),
        .tx_start (tx_start),
        .data     (tx_data),
        .tx       (serial),
        .tx_busy  (tx_busy)
    );

    // Receiver: listens to the same serial wire and rebuilds the byte
    uart_rx #(.CLKS_PER_BIT(CLKS_PER_BIT)) u_rx (
        .clk         (clk),
        .rst         (rst),
        .rx          (serial),
        .data        (rx_data),
        .rx_valid    (rx_valid),
        .frame_error (frame_error)
    );
endmodule