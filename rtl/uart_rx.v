module uart_rx #(parameter CLKS_PER_BIT = 868) (
    input  wire       clk,
    input  wire       rst,
    input  wire       rx,
    output reg  [7:0] data,
    output reg        rx_valid,
    output reg        frame_error
);
    localparam IDLE = 2'd0, START = 2'd1, DATA = 2'd2, STOP = 2'd3;

    reg [1:0] state;
    reg [9:0] timer;
    reg [2:0] bit_index;

    always @(posedge clk) begin
        if (rst) begin
            state <= IDLE; timer <= 0; bit_index <= 0;
            data <= 0; rx_valid <= 1'b0; frame_error <= 1'b0;
        end else begin
            rx_valid <= 1'b0;          // default: only pulse for one cycle

            case (state)
                IDLE: begin
                    timer <= 0;
                    bit_index <= 0;
                    if (rx == 1'b0)                          // wire dropped: start bit!
                        state <= START;
                end

                START: begin
                    if (timer == CLKS_PER_BIT/2 - 1) begin   // middle of start bit
                        timer <= 0;
                        if (rx == 1'b0)                      // still 0: real start bit
                            state <= DATA;
                        else                                 // back to 1: just a glitch
                            state <= IDLE;
                    end else
                        timer <= timer + 1;
                end

                DATA: begin
                    if (timer == CLKS_PER_BIT - 1) begin     // middle of next bit
                        timer <= 0;
                        data[bit_index] <= rx;               // read the wire
                        if (bit_index == 3'd7)               // that was the last bit
                            state <= STOP;
                        else
                            bit_index <= bit_index + 1;      // next bit
                    end else
                        timer <= timer + 1;
                end

                STOP: begin
                    if (timer == CLKS_PER_BIT - 1) begin     // middle of stop bit
                        timer <= 0;
                        if (rx == 1'b1) begin                // correct stop bit
                            rx_valid    <= 1'b1;
                            frame_error <= 1'b0;
                        end else                             // stop bit wrong
                            frame_error <= 1'b1;
                        state <= IDLE;
                    end else
                        timer <= timer + 1;
                end

                default: state <= IDLE;
            endcase
        end
    end
endmodule