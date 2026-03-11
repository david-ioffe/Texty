import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { useRouter } from "expo-router";

export default function LoginScreen() {
  const router = useRouter();

  function goToPhoneStep() {
    router.push("/(auth)/phone");
  }

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>ברוך הבא</Text>

        <Text style={styles.subtitle}>
          ההתחברות מתבצעת באמצעות מספר טלפון וקוד אימות שיישלח אליך ב-SMS
        </Text>

        <TouchableOpacity style={styles.primaryButton} onPress={goToPhoneStep}>
          <Text style={styles.primaryButtonText}>התחל אימות</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F8FAFC",
    justifyContent: "center",
    paddingHorizontal: 24,
  },
  content: {
    backgroundColor: "#FFFFFF",
    borderRadius: 24,
    padding: 28,
    shadowColor: "#000",
    shadowOpacity: 0.08,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 4 },
    elevation: 4,
  },
  title: {
    fontSize: 30,
    fontWeight: "700",
    textAlign: "center",
    color: "#0F172A",
    marginBottom: 14,
  },
  subtitle: {
    fontSize: 16,
    lineHeight: 24,
    textAlign: "center",
    color: "#475569",
    marginBottom: 28,
  },
  primaryButton: {
    backgroundColor: "#2563EB",
    paddingVertical: 16,
    borderRadius: 14,
    alignItems: "center",
  },
  primaryButtonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "600",
  },
});