`timescale 1 ps/1 ps
`define OK 12
`define INCORRECT 13


module stimulus_gen (
	input clk,
	output reg load,
	output reg[511:0] data,
	output reg[511:0] wavedrom_title,
	output reg wavedrom_enable
);


// Add two ports to module stimulus_gen:
//    output [511:0] wavedrom_title
//    output reg wavedrom_enable

	task wavedrom_start(input[511:0] title = "");
	endtask
	
	task wavedrom_stop;
		#1;
	endtask	



	initial begin
		data <= 0;
		data[0] <= 1'b1;
		load <= 1;
		@(posedge clk); wavedrom_start("Load q[511:0] = 1: See Hint.");
		@(posedge clk);
		@(posedge clk);
		load <= 0;
		repeat(10) @(posedge clk);		
		wavedrom_stop();
		
		data <= 0;
		data[256] <= 1'b1;
		load <= 1;
		@(posedge clk);
		@(posedge clk);
		@(posedge clk);
		load <= 0;
		repeat(1000) @(posedge clk) begin
		end
		data <= 512'h4df;
		load <= 1;
		@(posedge clk);
		load <= 0;
		repeat(1000) @(posedge clk) begin
		end
		data <= $random;
		load <= 1;
		@(posedge clk);
		load <= 0;
		repeat(1000) @(posedge clk) begin
		end

		data <= 0;
		load <= 1;
		repeat (20) @(posedge clk);
		@(posedge clk) data <= 2;
		@(posedge clk) data <= 4;
		@(posedge clk) begin
			data <= 9;
			load <= 0;
		end
		@(posedge clk) data <= 12;
		repeat(100) @(posedge clk);

		#1 $finish;
	end
	
endmodule

module tb();

	typedef struct packed {
		int errors;
		int errortime;
		int errors_q;
		int errortime_q;

		int clocks;
	} stats;
	
	stats stats1;
	
	
	wire[511:0] wavedrom_title;
	wire wavedrom_enable;
	int wavedrom_hide_after_time;
	
	reg clk=0;
	initial forever
		#5 clk = ~clk;

	logic load;
	logic [511:0] data;
	logic [511:0] q_ref;
	logic [511:0] q_dut;

	initial begin 
		$dumpfile("wave.vcd");
		$dumpvars();
	end


	wire tb_match;		// Verification
	wire tb_mismatch = ~tb_match;
	
	stimulus_gen stim1 (
		.clk,
		.* ,
		.load,
		.data );
	RefModule good1 (
		.clk,
		.load,
		.data,
		.q(q_ref) );
		
	TopModule top_module1 (
		.clk,
		.load,
		.data,
		.q(q_dut) );

	
	bit strobe = 0;
	task wait_for_end_of_timestep;
		repeat(5) begin
			strobe <= !strobe;  // Try to delay until the very end of the time step.
			@(strobe);
		end
	endtask	

	
	final begin
		if (stats1.errors_q) $display("Hint: Output '%s' has %0d mismatches. First mismatch occurred at time %0d.", "q", stats1.errors_q, stats1.errortime_q);
		else $display("Hint: Output '%s' has no mismatches.", "q");

		$display("Hint: Total mismatched samples is %1d out of %1d samples\n", stats1.errors, stats1.clocks);
		$display("Simulation finished at %0d ps", $time);
		$display("Mismatches: %1d in %1d samples", stats1.errors, stats1.clocks);
	end
	
	// Verification: XORs on the right makes any X in good_vector match anything, but X in dut_vector will only match X.
	assign tb_match = ( { q_ref } === ( { q_ref } ^ { q_dut } ^ { q_ref } ) );
	// Use explicit sensitivity list here. @(*) causes NetProc::nex_input() to be called when trying to compute
	// the sensitivity list of the @(strobe) process, which isn't implemented.
	always @(posedge clk, negedge clk) begin

		stats1.clocks++;
		if (!tb_match) begin
			if (stats1.errors == 0) stats1.errortime = $time;
			stats1.errors++;
		end
		if (q_ref !== ( q_ref ^ q_dut ^ q_ref ))
		begin if (stats1.errors_q == 0) stats1.errortime_q = $time;
			stats1.errors_q = stats1.errors_q+1'b1; end

	end

   // add timeout after 100K cycles
   initial begin
     #1000000
     $display("TIMEOUT");
     $finish();
   end

endmodule



module RefModule (
  input clk,
  input load,
  input [511:0] data,
  output reg [511:0] q
);

  always @(posedge clk) begin
    if (load)
      q <= data;
    else begin
      q <=
      ~((q[$bits(q)-1:1] & q[$bits(q)-1:0] & {q[$bits(q)-2:0], 1'b0}) |
      (~q[$bits(q)-1:1] & ~q[$bits(q)-1:0] & ~{q[$bits(q)-2:0], 1'b0}) |
      (q[$bits(q)-1:1] & ~q[$bits(q)-1:0] & ~{q[$bits(q)-2:0], 1'b0}) )
      ;
    end
  end

endmodule


module TopModule
(
  input  logic       clk,
  input  logic       load,
  input  logic [511:0] data,
  output logic [511:0] q
);

  logic [511:0] next_q;

  // 512-bit register to hold the state of the cellular automaton
  always @(posedge clk) begin
    if (load) begin
      q <= data;
    end else begin
      q <= next_q;
    end
  end

  // Combinational logic for Rule 110
  always @(*) begin
    for (int i = 0; i < 512; i++) begin
      logic left, center, right;
      center = q[i];
      if (i == 0) begin
        right = 0; // Boundary condition
        left = q[i+1];
      end else if (i == 511) begin
        left = 0; // Boundary condition
        right = q[i-1];
      end else begin
        left = q[i+1];
        right = q[i-1];
      end

      // Rule 110 logic
      case ({left, center, right})
        3'b111: next_q[i] = 1'b0;
        3'b110: next_q[i] = 1'b1;
        3'b101: next_q[i] = 1'b1;
        3'b100: next_q[i] = 1'b0;
        3'b011: next_q[i] = 1'b1;
        3'b010: next_q[i] = 1'b1;
        3'b001: next_q[i] = 1'b1;
        3'b000: next_q[i] = 1'b0;
      endcase
    end
  end

endmodule