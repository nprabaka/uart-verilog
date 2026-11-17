module uart_tx #(parameter CLKS_PER_BIT = 868) (
    input  wire       clk,
    input  wire       rst,
    input  wire       tx_start,
    input  wire [7:0] data,
    output reg        tx,
    output reg        tx_busy
);
    localparam IDLE = 2'd0, START = 2'd1, DATA = 2'd2, STOP = 2'd3;

    reg [1:0]  state;
    reg [9:0]  timer;
    reg [2:0]  bit_index;
    reg [7:0]  data_reg;

    wire timer_done = (timer == CLKS_PER_BIT - 1);

    always @(posedge clk) begin
        if (rst) begin
            state     <= IDLE;
            timer     <= 0;
            bit_index <= 0;
            tx        <= 1'b1;
            tx_busy   <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    tx        <= 1'b1;
                    tx_busy   <= 1'b0;
                    timer     <= 0;
                    bit_index <= 0;
                    if (tx_start) begin
                        data_reg <= data;
                        tx_busy  <= 1'b1;
                        state    <= START;
                    end
                end

                START: begin
                    tx      <= 1'b0;
                    tx_busy <= 1'b1;
                    if (timer_done) begin
                        timer <= 0;
                        state <= DATA;
                    end else
                        timer <= timer + 1;
                end

                DATA: begin
                    tx <= data_reg[bit_index];
                    if (timer_done) begin
                        timer <= 0;
                        if (bit_index == 3'd7)
                            state <= STOP;
                        else
                            bit_index <= bit_index + 1;
                    end else
                        timer <= timer + 1;
                end

                STOP: begin
                    tx <= 1'b1;
                    if (timer_done) begin
                        timer <= 0;
                        state <= IDLE;
                    end else
                        timer <= timer + 1;
                end

                default: state <= IDLE;
            endcase
        end
    end
endmodule