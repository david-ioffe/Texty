import { useState } from "react";
import {
 View,
 Text,
 TextInput,
 TouchableOpacity,
 StyleSheet,
 ActivityIndicator,
} from "react-native";
import { useRouter } from "expo-router";

export default function PhoneScreen() {

 const router = useRouter();

 const [phone, setPhone] = useState("");
 const [error, setError] = useState("");
 const [loading, setLoading] = useState(false);

 async function sendPhoneToBackend() {

   setError("");

   if (phone.length < 9) {
     setError("מספר טלפון לא תקין");
     return;
   }

   try {

     setLoading(true);

     const response = await fetch("http://10.0.0.16:8000/auth/send-code", {
       method: "POST",
       headers: {
         "Content-Type": "application/json"
       },
       body: JSON.stringify({
         phone: phone,
         recaptcha_token : null,
         captcha_response : null,
         client_type : null,
         recaptcha_version : null
       })
     });

     const data = await response.json();

     if (!response.ok) {
       setError(data.message || "השרת דחה את הבקשה");
       return;
     }

     router.push({
       pathname: "/(auth)/verify",
       params: { phone: phone }
     });

   } catch (e) {
    // "לא ניתן להתחבר לשרת"
     setError(e.message);

   } finally {

     setLoading(false);

   }

 }

 return (

   <View style={styles.container}>

     <Text style={styles.title}>
       התחברות
     </Text>

     <Text style={styles.subtitle}>
       הזן מספר טלפון לקבלת קוד
     </Text>

     <TextInput
       style={styles.input}
       placeholder="מספר טלפון"
       keyboardType="phone-pad"
       value={phone}
       onChangeText={setPhone}
     />

     {error !== "" && (
       <Text style={styles.error}>
         {error}
       </Text>
     )}

     <TouchableOpacity
       style={styles.button}
       onPress={sendPhoneToBackend}
       disabled={loading}
     >

       {loading
         ? <ActivityIndicator color="white" />
         : <Text style={styles.buttonText}>שלח קוד</Text>
       }

     </TouchableOpacity>

   </View>
 );
}

const styles = StyleSheet.create({

 container: {
   flex: 1,
   justifyContent: "center",
   padding: 24,
   backgroundColor: "white"
 },

 title: {
   fontSize: 32,
   fontWeight: "700",
   textAlign: "center",
   marginBottom: 10
 },

 subtitle: {
   textAlign: "center",
   color: "#666",
   marginBottom: 30
 },

 input: {
   borderWidth: 1,
   borderColor: "#ccc",
   borderRadius: 10,
   padding: 14,
   marginBottom: 10
 },

 error: {
   color: "#ff3b30",
   marginBottom: 10,
   textAlign: "center"
 },

 button: {
   backgroundColor: "#007AFF",
   padding: 15,
   borderRadius: 10,
   alignItems: "center"
 },

 buttonText: {
   color: "white",
   fontWeight: "600",
   fontSize: 16
 }

});