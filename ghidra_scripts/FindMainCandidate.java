// Finds likely user-code entry points after Ghidra auto-analysis.
//@category Crackme

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.BookmarkType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.symbol.SourceType;

public class FindMainCandidate extends GhidraScript {

	private static class Candidate {
		final Function function;
		final int score;
		final String reason;

		Candidate(Function function, int score, String reason) {
			this.function = function;
			this.score = score;
			this.reason = reason;
		}
	}

	@Override
	protected void run() throws Exception {
		List<Candidate> candidates = collectCandidates();
		if (candidates.isEmpty()) {
			println("[ghidra-main] no obvious main candidate found");
			return;
		}

		candidates.sort(Comparator
			.comparingInt((Candidate c) -> c.score)
			.reversed()
			.thenComparing(c -> c.function.getEntryPoint()));

		Candidate best = candidates.get(0);
		Address address = best.function.getEntryPoint();
		String message = best.function.getName() + " at " + address + " (" + best.reason + ")";

		currentProgram.getBookmarkManager().setBookmark(address, BookmarkType.ANALYSIS,
			"Main Candidate", message);
		try {
			createLabel(address, "main_candidate", false, SourceType.ANALYSIS);
		}
		catch (Exception e) {
			// Existing labels are fine; the bookmark and terminal hint are the useful parts.
		}

		println("[ghidra-main] best candidate: " + message);
		int printed = 0;
		for (int i = 1; i < candidates.size() && printed < 4; i++) {
			Candidate candidate = candidates.get(i);
			println("[ghidra-main] also consider: " + candidate.function.getName() + " at " +
				candidate.function.getEntryPoint() + " (" + candidate.reason + ")");
			printed++;
		}
	}

	private List<Candidate> collectCandidates() {
		List<Candidate> candidates = new ArrayList<>();
		FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
		for (Function function : functions) {
			Candidate candidate = score(function);
			if (candidate != null) {
				candidates.add(candidate);
			}
		}
		return candidates;
	}

	private Candidate score(Function function) {
		String name = function.getName();
		String raw = name.toLowerCase();
		String normalized = normalize(name);
		if (normalized.isEmpty()) {
			return null;
		}
		if (raw.equals("___main") || normalized.equals("libc_start_main")) {
			return null;
		}
		if (normalized.equals("winmain")) {
			return new Candidate(function, 100, "Windows user entry point");
		}
		if (normalized.equals("main")) {
			return new Candidate(function, 95, "C/C++ user entry point");
		}
		if (normalized.equals("wmain")) {
			return new Candidate(function, 90, "wide-character C/C++ user entry point");
		}
		if (normalized.equals("maincrtstartup") || normalized.equals("winmaincrtstartup")) {
			return new Candidate(function, 20, "CRT startup wrapper");
		}
		return null;
	}

	private String normalize(String name) {
		String normalized = name.toLowerCase();
		while (normalized.startsWith("_")) {
			normalized = normalized.substring(1);
		}
		normalized = normalized.replaceFirst("@[0-9]+$", "");
		return normalized;
	}
}
