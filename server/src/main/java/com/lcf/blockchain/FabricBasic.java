package com.lcf.blockchain;/*
							* Copyright IBM Corp. All Rights Reserved.
							*
							* SPDX-License-Identifier: Apache-2.0
							*/

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.lcf.pojo.Peer;
import io.grpc.ChannelCredentials;
import io.grpc.Grpc;
import io.grpc.ManagedChannel;
import io.grpc.TlsChannelCredentials;

import lombok.var;
import org.apache.ibatis.javassist.NotFoundException;
import org.hyperledger.fabric.client.*;
import org.hyperledger.fabric.client.identity.*;
import org.springframework.util.ResourceUtils;

import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.InvalidKeyException;
import java.security.PrivateKey;
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;

public final class FabricBasic {
	private static Path BASIC_PATH = null;
	private static Gateway gateway = null;
	private static Network network_ = null;
	static {
		try {
			BASIC_PATH = Paths.get("/", "home", "liang", "go", "src", "github.com", "liang512", "fabric-samples",
					"test-network", "organizations",
					"peerOrganizations", "org1.example.com");
			// BASIC_PATH = ResourceUtils.getURL("classpath:organizations").getPath();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	// 节点和负载信息
	public static ArrayList<Peer> peers = new ArrayList<>();
	public static int currentPeerId = 0;

	private static final String MSP_ID = System.getenv().getOrDefault("MSP_ID", "Org1MSP");
	private static String CHANNEL_NAME = System.getenv().getOrDefault("CHANNEL_NAME", "mychannel");
	private static String CHAINCODE_NAME = System.getenv().getOrDefault("CHAINCODE_NAME", "user");

	// Path to crypto materials.
	// private static final Path CRYPTO_PATH = BASIC_PATH;
	// Path to user certificate.
	private static final Path CERT_PATH = BASIC_PATH
			.resolve(Paths.get("users/User1@org1.example.com/msp/signcerts/User1@org1.example.com-cert.pem"));
	// Path to user private key directory.
	private static final Path KEY_DIR_PATH = BASIC_PATH
			.resolve(Paths.get("users/User1@org1.example.com/msp/keystore"));
	// Path to peer tls certificate.
	private static final Path TLS_CERT_PATH = BASIC_PATH.resolve(Paths.get(
			"peers/peer0.org1.example.com/tls/ca.crt"));

	// Gateway peer end point.
	private static final String PEER_ENDPOINT = "localhost:7051";
	// private static final String PEER_ENDPOINT = "localhost:7051";
	private static final String OVERRIDE_AUTH = "peer0.org1.example.com";

	private final Contract contract;
	private final String assetId = "asset" + Instant.now().toEpochMilli();
	private final Gson gson = new GsonBuilder().setPrettyPrinting().create();

	public static Gateway getGateway() {
		if (gateway == null) {
			try {
				gateway = fetchGateway();
				return gateway;
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
		return gateway;
	}

	public static Network getNetwork_() {
		return network_;
	}

	public static void main(final String[] args) throws Exception {
		// The gRPC client connection should be shared by all Gateway connections to
		// this endpoint.
		ManagedChannel channel = newGrpcConnection();

		Gateway.Builder builder = Gateway.newInstance().identity(newIdentity()).signer(newSigner()).connection(channel)
				// Default timeouts for different gRPC calls
				.evaluateOptions(options -> options.withDeadlineAfter(5, TimeUnit.SECONDS))
				.endorseOptions(options -> options.withDeadlineAfter(15, TimeUnit.SECONDS))
				.submitOptions(options -> options.withDeadlineAfter(5, TimeUnit.SECONDS))
				.commitStatusOptions(options -> options.withDeadlineAfter(1, TimeUnit.MINUTES));

		try (Gateway gateway = builder.connect()) {
			new FabricBasic(gateway).run();
		} finally {
			channel.shutdownNow().awaitTermination(5, TimeUnit.SECONDS);
		}
	}

	public static Gateway fetchGateway() throws Exception {

		ManagedChannel channel = newGrpcConnection();

		Gateway.Builder builder = Gateway.newInstance().identity(newIdentity()).signer(newSigner()).connection(channel)
				// Default timeouts for different gRPC calls
				.evaluateOptions(options -> options.withDeadlineAfter(5, TimeUnit.SECONDS))
				.endorseOptions(options -> options.withDeadlineAfter(15, TimeUnit.SECONDS))
				.submitOptions(options -> options.withDeadlineAfter(5, TimeUnit.SECONDS))
				.commitStatusOptions(options -> options.withDeadlineAfter(1, TimeUnit.MINUTES));

		try (Gateway gateway = builder.connect()) {
			return gateway;
		} catch (Exception e) {
			;
			channel.shutdownNow().awaitTermination(5, TimeUnit.SECONDS);
		}
		return null;
	}

	private static ManagedChannel newGrpcConnection() throws IOException {
		ChannelCredentials credentials = TlsChannelCredentials.newBuilder()
				.trustManager(TLS_CERT_PATH.toFile())
				.build();
		return Grpc.newChannelBuilder(PEER_ENDPOINT, credentials)
				.overrideAuthority(OVERRIDE_AUTH)
				.build();
	}

	private static Identity newIdentity() throws IOException, CertificateException {
		BufferedReader certReader = Files.newBufferedReader(CERT_PATH);
		X509Certificate certificate = Identities.readX509Certificate(certReader);

		return new X509Identity(MSP_ID, certificate);
	}

	private static Signer newSigner() throws IOException, InvalidKeyException {
		BufferedReader keyReader = Files.newBufferedReader(getPrivateKeyPath());
		PrivateKey privateKey = Identities.readPrivateKey(keyReader);

		return Signers.newPrivateKeySigner(privateKey);
	}

	private static Path getPrivateKeyPath() throws IOException {
		try (Stream<Path> keyFiles = Files.list(KEY_DIR_PATH)) {
			return keyFiles.findFirst().orElseThrow(() -> new IOException("记录不存在"));
		}
	}

	private String prettyJson(final byte[] json) {
		return prettyJson(new String(json, StandardCharsets.UTF_8));
	}

	private String prettyJson(final String json) {
		JsonElement parsedJson = JsonParser.parseString(json);
		return gson.toJson(parsedJson);
	}

	/**
	 * This type of transaction would typically only be run once by an application
	 * the first time it was started after its initial deployment. A new version of
	 * the chaincode deployed later would likely not need to run an "init" function.
	 */
	private void initLedger() throws EndorseException, SubmitException, CommitStatusException, CommitException {
		System.out.println(
				"\n--> Submit Transaction: InitLedger, function creates the initial set of assets on the ledger");

		contract.submitTransaction("InitLedger");

		System.out.println("*** Transaction committed successfully");
	}

	/**
	 * Evaluate a transaction to query ledger state.
	 */
	private void getAllAssets() throws GatewayException {
		System.out.println(
				"\n--> Evaluate Transaction: GetAllAssets, function returns all the current assets on the ledger");

		byte[] result = contract.evaluateTransaction("GetAllAssets");

		System.out.println("*** Result: " + prettyJson(result));
	}

	public FabricBasic(final Gateway gateway) {
		// Get a network instance representing the channel where the smart contract is
		// deployed.
		Network network = gateway.getNetwork(CHANNEL_NAME);
		network_ = network;
		// Get the smart contract from the network.
		contract = network.getContract(CHAINCODE_NAME);
		// 初始化peer节点列表和负载
		Peer peer1 = new Peer(0, 0, "peer0");
		Peer peer2 = new Peer(0, 0, "peer1");
		peers.add(peer1);
		peers.add(peer2);
	}

	public void run() throws GatewayException, CommitException {
		// Initialize a set of asset data on the ledger using the chaincode 'InitLedger'
		// function.
		// initLedger();

		// Return all the current assets on the ledger.
		getAllAssets();

		// // Create a new asset on the ledger.
		// createAsset();
		//
		// // Get the asset details by assetID.
		// readAssetById();

	}
}
