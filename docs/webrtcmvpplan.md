Implementation Plan: WebRTC Voice AI Pipeline (MVP with Pipecat)
LiveKit WebRTC Transport (Bidirectional Audio)

Transport Setup: Use Pipecat’s native LiveKitTransport to handle real-time bidirectional audio between the browser and backend
GitHub
. This built-in transport natively supports 16 kHz mono PCM audio streams (matching our STT/TTS requirements) and integrates seamlessly with Pipecat’s pipeline architecture
GitHub
. LiveKit provides production-ready WebRTC connectivity with low latency (~150–300 ms added) and full on-prem control
GitHub
. It also supports Smart-Turn v2 natively for turn-taking.

Server Configuration: Add a LiveKit server service to Docker Compose for local deployment. Use the official livekit/livekit-server image and expose ports (e.g. 7880 for WebRTC, 7881 for TURN) as needed
GitHub
. Configure it for 16 kHz audio and mono channel to align with pipeline settings (the default supports Opus at 16 kHz; you can enforce this in LiveKit config)
GitHub
. For local MVP, you can use development API keys in LiveKit’s config or environment.

Pipecat Integration: In the Python backend, initialize the transport via Pipecat’s LiveKit client utilities. For example, use pipecat.runner.livekit.configure() to obtain the LiveKit url, token, and room_name, then create LiveKitTransport(url=url, token=token, room_name=room, params=LiveKitParams(...))
GitHub
. In LiveKitParams, enable audio in/out (audio_in_enabled=True, audio_out_enabled=True) and set audio_in_sample_rate=16000 (and same for output) to ensure no resampling
GitHub
. Attach the VAD and Smart Turn analyzers in the transport params (see Turn Detection below).

Client Integration: Use the LiveKit JS SDK in the browser to capture and play audio streams. Configure the client’s audio capture for 16 kHz mono as well (LiveKit’s API allows specifying audioCaptureDefaults.sampleRate = 16000 and channelCount = 1)
GitHub
. Enable echo cancellation and noise suppression on the client side
GitHub
 for better quality. The browser client will join a LiveKit room with a token, and audio will flow to/from the Pipecat LiveKitTransport in real time.

Notes: The LiveKit transport abstracts away WebRTC complexities – it will provide incoming audio frames into the Pipecat pipeline and accept outgoing audio frames for playback. Because it’s self-hosted, there’s no external latency beyond our network, helping keep round-trip times within ~650–750 ms in total
GitHub
 for the MVP. We leverage Pipecat’s native integration (no custom WebRTC code needed)
GitHub
.

Turn Detection and Barge-in (Smart-Turn v2 + VAD)

Voice Activity Detection: Incorporate Silero VAD (via Pipecat’s VAD processor) to continuously detect speech vs. silence on the incoming audio stream. VAD will operate on ~20–30 ms audio frames
GitHub
 and output events when speech starts/stops. Configure the VAD with a short silence timeout (stop_secs ≈ 0.2s) and a suitable threshold (e.g. 0.5) so that it quickly signals the end of a user utterance
GitHub
. This short pause detection is tuned for Turkish turn-taking (users often pause briefly at sentence boundaries)
GitHub
. The VAD’s job is to minimize unneeded processing by gating the STT/LLM when the user isn’t speaking, and to assist Smart-Turn in barge-in detection.

Smart-Turn v2 Analyzer: Use Pipecat’s SmartTurnV2 turn-taking analyzer to decide when a speaker’s turn is complete and manage interruptions. Smart-Turn v2 is an ML model (~95M params) optimized for conversational cues
GitHub
. It detects Turkish intonation patterns, filler words (“yani”, “şey”, etc.), and other cues to determine if the user is pausing or finished
GitHub
. It outputs a probability of turn completion (<100 ms inference time) and enables context-aware barge-in (can signal an interruption within ~300 ms of the user starting to speak over the assistant)
GitHub
. For the MVP, instantiate LocalSmartTurnAnalyzerV2 (PyTorch-based) and specify turkish_optimized=True if available, so it uses Turkish language support built into the model
GitHub
.

Integration in Pipeline: Attach Smart-Turn to the audio stream via Pipecat’s transport params. In the LiveKitTransport’s params, set turn_analyzer=LocalSmartTurnAnalyzerV2() and vad_analyzer=<SileroVAD> so that incoming audio frames are analyzed by both
GitHub
. The VAD provides a first layer of detection, and Smart-Turn uses a longer audio window (~8 seconds, up to 16s max) to make robust decisions
GitHub
. Pipecat’s transport will emit events/frames when the user has finished talking (UserStoppedSpeakingFrame or turn-complete event) which we use to trigger the LLM response. Barge-in: Also configure allow_interruptions=True on the pipeline/task
GitHub
 to allow the user to interrupt the assistant. With this, if the user starts speaking during the assistant’s TTS output, the Smart-Turn + VAD will detect the user’s speech immediately and Pipecat can halt or pause the TTS output.

Turkish Support: No special training needed beyond using the Smart-Turn v2 model (which already supports Turkish with >90% turn accuracy
GitHub
). However, we tune parameters for Turkish conversation: e.g. set VAD start_secs around 0.1s for quick voice onset detection, and possibly adjust Smart-Turn’s threshold (probability 0.5 or slightly higher if needed) to avoid false positives in fast Turkish speech
GitHub
. The system will naturally handle filler words and polite interjections common in Turkish, improving barge-in decisions (e.g. distinguishing a polite “kusura bakmayın...” from a real interruption)
GitHub
.

Configuration Tip: During development, enable debug logs for turn detection to see when VAD thinks speech started/ended and when Smart-Turn declares a turn completion. This will help fine-tune the stop_secs and threshold. For example, you should see logs like “Smart Turn: COMPLETE, Probability: 0.95…” or “Barge-in Triggered: user_energy=0.75, assistant_interrupted=true” during tests, confirming the timing
GitHub
.

Speech-to-Text: Vosk Streaming STT (CPU)

STT Engine: Use Vosk for real-time Turkish speech recognition. Vosk offers an offline model vosk-model-tr-0.3 specialized for Turkish
GitHub
. It runs entirely on CPU and can provide streaming transcriptions with partial results (words as the user speaks) and final transcripts at utterance end
GitHub
. Importantly, it’s lightweight enough for 16 kHz audio and can return partial text with low latency (<500 ms for partial updates in tests)
GitHub
.

Integration Options: There are two ways to integrate Vosk in our pipeline:

In-Process (Python): Use Pipecat’s VoskSTTService to load the model in the pipeline process. On pipeline start, it will initialize the Vosk model and recognizer with the given model files
GitHub
GitHub
. As audio frames flow in, the service feeds them to Vosk. We enable partial_results=True so that as soon as Vosk has a guess, it yields an InterimTranscriptionFrame (partial text) for downstream components
GitHub
GitHub
. When Vosk recognizes end-of-speech (or the VAD indicates stop), it yields a final TranscriptionFrame with the complete utterance
GitHub
. We configure the service with sample_rate=16000 and the path to the Turkish model. The Pipecat config can also set a confidence_threshold (e.g. 0.8) so low-confidence junk is ignored
GitHub
.

External Service: Alternatively, run Vosk’s HTTP server (e.g. using alphacep/kaldi-vosk-server Docker). In this case, use Pipecat’s StreamingVoskSTTService to send audio to the server’s WebSocket API
GitHub
GitHub
. For MVP simplicity, in-process is recommended (fewer moving parts), but the external approach allows isolating STT load (you could allocate it more CPU cores or run on a separate machine if needed). Both approaches support streaming mode equivalently.

Configuring Vosk: Download the vosk-model-tr-0.3 model and mount it in the Docker container or make it accessible to the Python process (e.g., in a volume at /models/vosk-model-tr-0.3). The model is ~1.4GB, so ensure enough memory. If running via Docker Compose, you could define a volume for the model. In Pipecat, instantiate Vosk with the model path and language code "tr-TR". No GPU is used – Vosk is CPU-optimized. It may use around 1–2 CPU cores per stream; for MVP this is fine.

Output Handling: The STT service will emit text frames that contain the recognized utterance. We will feed these into the LLM. Each TranscriptionFrame can include metadata like a timestamp or confidence. We should accumulate partial transcripts if needed – e.g., Pipecat’s context aggregator (next section) can combine them or update the user’s interim transcript in real-time. For MVP, we can simply use the final transcript for generating a response, but partials can be logged or even echoed to the user interface if we had one (not required, but it shows responsiveness).

Turkish Accuracy: Vosk’s model provides decent accuracy for general Turkish. We might later consider fine-tuning or using alternative STT (like OpenAI Whisper) for better results, but Whisper is slower on CPU. For now, Vosk strikes a good balance. It will handle Turkish-specific characters and words natively. Just ensure that the audio is clearly 16 kHz PCM and not compressed (our pipeline ensures raw PCM frames from WebRTC).

Error Handling: Implement fallback logic if STT fails (e.g., no transcription after a timeout). Pipecat allows a fallback STT service configuration
GitHub
GitHub
. For MVP, we might not need a secondary STT, but we should handle cases like an empty transcript (perhaps treat it as “no input detected”).

Language Model: GPT-OSS-20B on GPU (LLM Service)

Model Choice: The core conversational AI will be GPT-OSS-20B, an open-source 21-billion-parameter model from OpenAI’s open-weight series. This model is designed to run on consumer-grade hardware (it uses a Mixture-of-Experts architecture: only ~3.6B parameters activate per inference)
govinfosecurity.com
, making it feasible to run on a single high-end GPU. We have an NVIDIA RTX 4060 Ti (8GB VRAM), which is below the model’s nominal 16GB memory footprint
govinfosecurity.com
. Therefore, we will employ model quantization and efficient serving techniques to fit and run it.

Serving Method: We have two primary options to serve GPT-OSS-20B:

Hugging Face Transformers (with Quantization): Load the model using the Hugging Face transformers library with 4-bit quantization (e.g., using bitsandbytes or GPTQ). This can compress the model significantly – given only a subset of parameters are active, a 4-bit quant should allow 8GB to handle it (active 3.6B params * 4 bits ≈ 1.8GB, plus overheads)
govinfosecurity.com
. We can use AutoModelForCausalLM.from_pretrained(...) with load_in_4bit=True or similar, and place it on GPU. This approach would run the model in-process. We must ensure generation calls yield tokens incrementally (using generate(..., stream=True) or by manually iterating through model outputs) so we can stream responses.

Llama.cpp / Ollama (GGUF Quantized): Alternatively, use a lighter-weight inference engine like llama.cpp. We would convert the GPT-OSS-20B weights to a GGUF or similar format and run a dedicated server (or subprocess) that can generate text given a prompt. Pipecat has support for local LLM services (e.g., OLLamaLLMService for models served by Ollama, which internally can use llama.cpp)
docs.pipecat.ai
. This might be preferred if Python GPU memory is a concern – llama.cpp can offload to CPU or partially use GPU and is optimized for high throughput with quantized models. The architecture already envisions using llama.cpp for local models (e.g., they ran a 1.8B Qwen model via llama.cpp in development)
GitHub
, so hooking GPT-OSS-20B in similarly is feasible.

Pipecat Integration: Wrap the LLM in a Pipecat service so it fits into our pipeline. Pipecat provides an OpenAILLMService interface and context aggregation utility. For MVP, we can implement a simple custom LocalLLMService that calls our model (either via Transformers or via an API to the external service) and yields a TextFrame containing the assistant’s response. The key is to stream tokens as they are generated: as the model produces output text, we should yield partial text frames. This allows the TTS stage to begin speaking the answer before the model has generated the entire sentence, significantly cutting perceived latency
GitHub
. For example, if using Transformers, we can generate with do_sample=False, max_new_tokens=N and use the generate method with a callback or token generator. If using llama.cpp, we can read its token stream from stdout or its API. Each token or sentence can be sent as a TextFrame down the pipeline.

Prompt & Context: Since this is a voice assistant, we likely want to wrap the user’s transcribed input into a system prompt or conversation context. We might include a system prompt like “You are a helpful assistant...” in the LLM prompt (this can be coded in the LocalLLMService). The Pipecat context aggregator can maintain the chat history – for MVP, we can keep it simple (perhaps just the last user query for now, or none at all). But if multi-turn conversation is expected, we’d use a context aggregator to supply recent dialogue to the LLM each turn
GitHub
. (This was indicated in the architecture, but can be added later if needed.)

GPU Utilization: Running GPT-OSS-20B on the RTX 4060 Ti will utilize the GPU for matrix multiplies. We should ensure the Docker Compose setup includes the NVIDIA runtime (so the container can access the GPU). In the Compose file, under the Pipecat service, add deploy.runtime: nvidia or use --gpus if running via CLI. Because the model is large, ensure no other heavy GPU processes are running simultaneously (8GB is fully needed). If memory is still an issue at 4-bit, we can offload some layers to CPU (Transformers device_map="auto" can offload lower attention layers to system RAM as needed).

Latency Expectations: GPT-OSS-20B is powerful but inference speed will be a consideration. With 8GB and 4-bit, we might get on the order of a few tokens per second if running on GPU. To keep conversation responsive, we should limit the length of responses (focus on concise answers). The user’s utterances likely don’t require very long answers, which helps. Also, because we stream tokens, the user will start hearing the answer after the first token is generated (perhaps ~200–500 ms for the first token, then continuing). This is acceptable in the ~800ms target window. We will test with sample queries and if it’s too slow, consider reducing model size or complexity for MVP (e.g. use the 1.8B model as fallback).

Testing: Use simple prompts in Turkish to verify the model’s output quality. GPT-OSS-20B was primarily trained on English
govinfosecurity.com
, so it might not be fluent in Turkish by default. If that’s the case, we might swap in a Turkish-optimized model (like a smaller Turkish LLaMA or Qwen 7B that the architecture used
GitHub
) for the MVP. However, if GPT-OSS has multilingual capabilities, we will proceed. We can also constrain the LLM output length and set it to be more factual or concise via the system prompt to avoid long rambling outputs that increase latency.

Text-to-Speech: Piper Streaming TTS (CPU)

TTS Engine: Use Piper for on-premises Turkish text-to-speech. Piper is a lightweight, high-quality TTS that supports various voices. We will use a Turkish voice model such as "tr_TR-dfki-medium" (this voice has a good balance of quality and speed). Piper runs on CPU and can generate 22 kHz or 16 kHz audio. We’ll configure it for 16 kHz mono output to stay consistent with the pipeline.

Deployment: Run Piper as a local TTS server. We can include an official Piper Docker image or build one. (Mozilla’s TTS repo or OHF-Voice’s Piper may provide a Docker; if not, we can run the Piper binary directly on the host or in a container.) The Piper HTTP API listens on a port (e.g., 5000) and accepts JSON with text, returning a WAV audio stream. In Docker Compose, add a service piper using an image that contains the Turkish model. Mount the model file if needed. Ensure this service starts before the Pipecat service.

Pipecat Integration: Use PiperTTSService in Pipecat to connect to the Piper server
reference-server.pipecat.ai
reference-server.pipecat.ai
. Initialize it with the base_url of the Piper HTTP endpoint (e.g., http://piper:5000/synthesize if using defaults) and an aiohttp session. Pipecat’s TTS service will send the text and stream back audio. We enable streaming mode for TTS: Piper can stream the WAV bytes as they are generated, and the Pipecat service will yield audio frames on the fly. For example, as soon as Piper produces ~200 ms of audio, Pipecat will strip the WAV header and emit a TTSAudioRawFrame for that chunk
reference-server.pipecat.ai
. This means the user starts hearing the speech while the rest is still being synthesized, keeping latency low
GitHub
. In code, when creating the TTS service (via a factory or directly), set streaming=True and specify the voice/language
GitHub
.

Audio Format: Piper’s outputs will be PCM audio frames. We should specify the sample rate if Piper doesn’t default to 16 kHz. (Many Piper voices output 22050 Hz; we can downsample or possibly Piper has a flag for output rate.) It’s easiest to run Piper to output at 16 kHz directly to avoid runtime resampling – many models have a native sample rate, which might be fine if slightly off (e.g., 22 kHz audio can be fed to Pipecat but then it wouldn’t match the 16 kHz input; let’s try to align it by choosing a model or adjusting settings).

Barge-in Support: Since we allow interruptions, we need TTS to be stoppable mid-stream. Pipecat’s pipeline will handle this if configured. When an interruption event occurs, we should instruct the TTS service to stop generating further audio (or simply stop reading further chunks). In practice, if using the Piper HTTP stream, we might need to close the connection or have Piper stop. One approach: Pipecat could simply drop outgoing audio frames if a barge-in happens. For MVP, an easy method is to monitor for a UserStartedSpeakingFrame while TTS is playing and, if detected, immediately stop sending any new TTS frames to the output (and potentially call a reset on the TTS service). Pipecat’s allow_interruptions=True setting is meant to facilitate this
GitHub
.

Quality and Performance: Piper on CPU is quite fast (especially for shorter sentences). It should synthesize a short sentence (e.g. 10-15 words) in under 200 ms on a modern CPU. With streaming, the user might get the first audio chunk in ~100 ms. We will fine-tune Piper’s behavior if needed (it has settings like prosody, speed that we can adjust via its SSML or API). For a natural experience, we might not want Piper to speak too fast even if we can, but some slight speed-up could help responsiveness. We’ll test with the chosen Turkish voice and adjust as necessary.

Logging: It’s useful to log the text being sent to TTS and maybe mark in logs when TTS audio starts and finishes. This will help correlate any gaps or delays in the audio pipeline.

Pipecat Pipeline Assembly (Full-Duplex Orchestration)

Pipeline Structure: We will construct the processing pipeline using Pipecat’s Pipeline class to wire together all components in order
GitHub
GitHub
. The high-level flow is: LiveKit audio input → VAD/SmartTurn (turn detection) → STT (speech to text) → LLM (generate response) → TTS (synthesize speech) → LiveKit audio output
GitHub
. In code, this might look like:

pipeline = Pipeline([
    transport.input(),      # incoming AudioRawFrame from LiveKit:contentReference[oaicite:57]{index=57}
    vad_processor,          # analyze frames, emit speech start/stop events
    stt_service,            # Audio → TranscriptionFrame (partial/final):contentReference[oaicite:58]{index=58}
    context_mgr.user(),     # (optional) format user transcript into LLM prompt
    llm_service,            # generate TextFrame(s) response (streaming tokens):contentReference[oaicite:59]{index=59}
    tts_service,            # Text → TTSAudioRawFrame(s):contentReference[oaicite:60]{index=60}
    transport.output(),     # send audio out via LiveKit
    context_mgr.assistant() # (optional) store assistant response in context
])


We will reuse the Pipecat service classes for each stage (e.g., SileroVADProcessor, VoskSTTService, LocalSmartTurnAnalyzerV2, PiperTTSService) rather than writing them from scratch – this reuse-first approach leverages the user’s existing pipecat repo implementations.

Full-Duplex Operation: The pipeline is inherently asynchronous and full-duplex. The transport.input() and transport.output() are running concurrently – Pipecat will not block one for the other. For example, the user can be speaking (producing audio frames into the pipeline) at the same time the assistant’s TTS is sending out frames. The Smart-Turn mechanism mediates turn-taking: if the user talks while the assistant is speaking, the pipeline will detect it and can cut off the TTS. Conversely, when the user falls silent, the pipeline triggers the LLM and TTS to respond. Both read and write audio streams are open simultaneously, enabling natural interruption and overlap.

Context and State: We include a context manager (context_mgr above) primarily to format and store conversation state. For MVP, this could simply package the user’s text into a prompt for the LLM (for example, add a prefix like “User: ...\nAssistant: ”) and later store the assistant’s reply. This is not strictly required for a single-turn demo, but it’s good practice and will be useful as we expand to multi-turn dialogues. The context manager could also enforce any system persona (e.g., always prepend a system message “You are a banking assistant…” as seen in development code)
GitHub
.

Pipeline Execution: We will wrap the pipeline in a Pipecat PipelineTask or runner. For example, Pipecat might provide a PipelineRunner to start the loop. We ensure PipelineParams(allow_interruptions=True) is set on the task so that interruption frames are honored
GitHub
. In local testing, we can run this pipeline task in an asyncio event loop (perhaps Pipecat does that internally). Essentially, once the user joins the LiveKit room and audio flows, the pipeline will be activated and run indefinitely handling audio in/out until the session ends.

Concurrency Considerations: Each voice session (each user connection) will instantiate its own pipeline. For the MVP on a single machine, we’ll likely handle one session at a time due to resource limits (the 20B model will use most of the GPU). However, Pipecat is designed to allow multiple pipelines/tasks to run concurrently if needed. If we did have multiple users, the LiveKitTransport would manage separate rooms or participants and we’d spin up a pipeline per participant. The architecture supports 50+ concurrent sessions in production
GitHub
, but for MVP we focus on correctness and real-time performance in one session. We should, however, design the pipeline code in a way that doesn’t use global state and can be instantiated per session easily.

Error Propagation: Pipecat pipelines propagate frames and can propagate errors (as ErrorFrame). We will ensure to handle exceptions in each component so the pipeline doesn’t crash on a transient error. For instance, if STT fails to process a frame, log it and continue; if LLM times out or errors, maybe send a fallback text (“Üzgünüm, bunu anlayamadım”) to TTS. This will make the MVP more robust during testing.

Latency and Performance Considerations

End-to-End Latency Target: Aim for end-to-end response latency under 800 ms, which is the project’s target for real-time feel
GitHub
. This means from the moment the user finishes speaking to the start of the assistant’s spoken reply should be well below 1 second. Each component in the pipeline contributes some latency; by designing for streaming and parallelism, we overlap operations to shrink the total time.

Latency Breakdown: Roughly: WebRTC transport ~150–200 ms network and jitter buffer latency
GitHub
, VAD/SmartTurn ~10–100 ms to decide end-of-utterance
GitHub
, STT partial result within ~0.5 s during speech
GitHub
 (and final result almost immediately after speech ends), LLM first token in perhaps 300 ms (on GPU, small prompt) and full answer maybe a few hundred ms more, TTS synthesis ~200 ms (with first audio chunk in ~100 ms). Many of these happen in parallel or stream: for example, STT is working while the user is still talking, so by the time the user stops, we may already have most of the transcription. Similarly, TTS starts speaking while the LLM is still finishing the tail of the text. By overlapping these stages, the perceived round-trip latency (user stop to voice start) will approach the largest single component delay rather than the sum of all.

Streaming & Overlap: Frame timing is critical. Use small audio frame sizes (20–30 ms) from the start so that we detect speech segments quickly
GitHub
. The pipeline processes frames asynchronously – Pipecat’s design is non-blocking
GitHub
. This means the STT can process the previous 20 ms of audio while the next 20 ms is still being captured, etc. When the user pauses, SmartTurn will cut off the incoming stream promptly thanks to the short VAD stop window
GitHub
. Then the LLM generation and TTS output proceed concurrently: the LLM streams out tokens, and as soon as a token or phrase is ready, TTS turns it into sound. We effectively create a pipeline parallelism where parts of the user’s utterance are being transcribed while later parts are still being spoken, and parts of the assistant’s answer are being spoken out while later parts are still being generated.

Concurrency & Threading: We need to ensure that heavy compute tasks do not block the entire pipeline. Pipecat likely runs each processor in the pipeline as an async coroutine. For CPU-bound tasks (like Vosk STT and Piper TTS), it might be okay since they yield control when awaiting I/O or next frame. The GPU-bound LLM generation might need special handling: if using Transformers without an async interface, it could block. To avoid this, we can offload LLM generation to a separate event loop or thread. One strategy: use Python’s asyncio.to_thread to run the blocking generate function in a thread, and have it yield tokens via a queue. This way the main loop isn’t stalled – important because otherwise incoming audio or other events might be delayed. We should verify Pipecat’s LLM service approach; if it already supports asynchronous token streaming (e.g., via callbacks), leverage that.

Resource Usage: On the CPU side, the STT and TTS will consume CPU cycles. Monitor their usage and consider pinning threads or adjusting priorities if needed (for instance, ensure the VAD/SmartTurn which are lightweight run in real-time to catch barge-in quickly, whereas TTS can be slightly lower priority). The GPU will be primarily used by the LLM. Memory is the biggest constraint – we addressed that with quantization. Also note that GPU inference can be made faster by using lower precision (which we do) and possibly enabling tensor cores (FP16 or INT8). We might experiment with TensorRT or other optimization if needed, but that’s likely beyond MVP scope.

Scalability (Beyond MVP): While not required now, it’s worth noting that the architecture can scale by separating components into microservices or using multiple GPUs. For concurrency, one could run multiple smaller LLM instances or queue LLM requests if many users speak simultaneously. For now, keep things simple: one conversation at a time, and optimize that path.

Logging and Telemetry (Local Debugging)

Verbose Logging: Since we are not using full Prometheus/Grafana in the MVP, we rely on logs for insight. Run the pipeline with debug-level logging enabled. Pipecat uses Python’s logging (or loguru); we’ll set log level to DEBUG for our services. This will print detailed messages from each component. For example, Vosk STT prints partial and final transcripts to the log
GitHub
, Smart-Turn prints turn decisions
GitHub
, and Piper TTS logs when it starts/stops and any errors
reference-server.pipecat.ai
reference-server.pipecat.ai
. These logs help trace the flow end-to-end.

Key Events to Log: We will add our own log statements around critical events:

When VAD detects speech start and end (e.g., log “User started speaking” and “User stopped speaking after X seconds”).

The final recognized text from STT (log the text string).

When LLM generation begins and ends, and possibly the generated text (though for long text, maybe truncate it in log). Also log timestamps to measure how long the LLM took.

When TTS starts speaking and finishes, and if applicable, when it’s interrupted.

Any barge-in events (log “Barge-in: user interrupted at 1.2s of assistant speech”).

Pipeline timing info: we can timestamp each stage to see cumulative latency. For instance, log the time difference between end-of-speech detection and start of TTS audio out.

Error Logging: Ensure exceptions in any async task are caught and logged. Use try/except around the LLM call especially, to log errors from the model. The Pipecat framework might convert unhandled exceptions to ErrorFrames; we can log those frames too.

Temporary Telemetry: We can use simple counters/timers for debugging performance. For example, record how many audio frames per second we process, or how many tokens per second the LLM is generating. This can be done by storing timestamps or using Python’s time.time() differences in strategic places, then printing the results. This is ad-hoc but useful to verify we meet real-time constraints.

No External Monitoring: We explicitly exclude Prometheus and database logging in the MVP, so we won’t set up any remote metrics. If Pipecat has any metric collectors, we’ll disable them for now (e.g., enable_metrics=False in pipeline params except for perhaps timing within components if it doesn’t add overhead). This keeps the system lean. Once the MVP is confirmed working, we can later introduce Prometheus hooks.

Using Tools: Leverage any built-in Pipecat observability for local runs. Pipecat might have an option to dump pipeline traces or save audio frames to files for analysis. For debugging audio issues, we could have the pipeline record incoming audio and outgoing audio to WAV files (just for test sessions) to listen back and ensure quality (this could be done by inserting a simple file-writer processor in parallel). But only do this in a controlled dev environment.

Testing and Tuning: As we assemble the system, perform iterative tests: start the Docker Compose, connect with a browser, say a sample sentence in Turkish, and observe logs. We should see: VAD triggers, STT partial prints, final text, LLM text, then TTS audio (perhaps play out on the browser). Any significant delay, gap, or mis-sequencing in logs will indicate where to adjust (e.g., if STT final comes long after speech, maybe VAD stop_secs too high; if TTS starts late, maybe LLM generation is slow – consider limiting output length or using a smaller model). Use the logs to verify that full-duplex is working (e.g., speak over the assistant and check that logs show the interruption and the assistant stops speaking promptly).

Conclusion: Full-Duplex Pipecat Orchestration in Turkish

By following this plan, we will implement a modular voice AI pipeline that reuses proven components from the Pipecat framework and integrates them for a Turkish conversation agent. The LiveKit transport provides the real-time audio stream interface
GitHub
, while Smart-Turn v2 and VAD together handle natural turn-taking and barge-in in Turkish conversations
GitHub
. Vosk STT on CPU will transcribe user speech with low latency
GitHub
, and the GPT-OSS-20B model on GPU will generate intelligent responses, served efficiently via quantization
GitHub
govinfosecurity.com
. Piper TTS on CPU will synthesize the assistant’s voice in Turkish and stream it back to the user with minimal delay
GitHub
. All these components are orchestrated in Pipecat’s asynchronous pipeline, enabling full-duplex interaction – the user and AI can speak and listen at the same time, making interruptions and natural dialogue flow possible. The MVP will run locally via Docker Compose, and we’ll utilize logging for monitoring system behavior. This foundation will allow developers for each module (transport, STT, LLM, TTS, etc.) to work in parallel, with clear integration points and configuration tips to ensure the pieces fit together.