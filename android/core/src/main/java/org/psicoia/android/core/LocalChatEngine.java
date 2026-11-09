package org.psicoia.android.core;

/** A runtime adapter must generate locally; this interface has no network/provider configuration. */
public interface LocalChatEngine {
    String generate(String prompt) throws Exception;
}
